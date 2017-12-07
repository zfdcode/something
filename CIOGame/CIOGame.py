import csv
import numpy as np
import pandas as pd
from matplotlib import pyplot as plt
from matplotlib import cm as cm
from gurobipy import *


class CIOGame:
    def __init__(self, periods=0):
        self.periods = periods
        print("Created CIOGame Object for period %s" % (str(periods)))

    def read_from_exel(self, filename='Kennzahlen_Tool.xlsm'):
        # Load spreadsheet
        xl = pd.ExcelFile(filename)

        # read management overview
        df_management_overview = xl.parse('Management Overview').rename(
            index=str, columns={"Unnamed: 2": ""}).set_index('').iloc[:, 3:(4 + self.periods)]
        df_management_overview = df_management_overview.loc[[
            "Car Financing Loans",
            "Customer Savings",
            "Requests to be processed LowPriceCars",
            "Requests to be processed MidPriceCars",
            "Requests to be processed HighPriceCars",
            "Contracts succeeded LowPriceCars",
            "Contracts succeeded MidPriceCars",
            "Contracts succeeded HighPriceCars",
            "Service Transactions to be processed loans",
            "Service Transactions succeeded loans",
            "Requests to be processed savings",
            "Contracts succeeded savings",
            "Service Transactions succeeded savings"
        ]]
        df_management_overview.columns = df_management_overview.columns.astype(
            str)

        # read balanced score card
        df_balanced_score_card = xl.parse('Balanced Score Card').rename(
            index=str, columns={"Unnamed: 2": ""}).set_index('').iloc[:, 4:(5 + self.periods)]
        df_balanced_score_card = df_balanced_score_card.loc[[
            "Customer Satisfaction",
            "Marketing Efficiency for product Car Financing Loans",
            "Marketing Efficiency for product Savings Account",
        ]]

        # read resource management
        rename_dict = {"Unnamed: 2": ""}
        loc_list = []
        for i in range(self.periods + 1):
            rename_dict.update({"P%g" % (i): str(i)})
            loc_list.append(str(i))
        df_resource_management = xl.parse('Resource Management').rename(
            index=str, columns=rename_dict).set_index('').loc[:, loc_list]
        df_resource_management = df_resource_management.loc[[
            "Marketing Expenditures Global",
            "Marketing Expenditures Product Loans",
            "Marketing Expenditures Product Savings",
            "Interest Rate Car Financing Loans",
            "Interest Rate Customer Savings"
        ]]

        return pd.concat([
            df_management_overview,
            df_balanced_score_card,
            df_resource_management
        ])

    def find_best_regr(self, X, y, df_pre, y_pre):
        diff = []
        regr_list = []
        data_size = len(y)
        # train the regrs
        for i in range(data_size):
            a = list(range(data_size))
            del a[i]
            X_train = X.iloc[a]
            X_test = X.iloc[i].values.reshape(1, -1)
            y_train = y[a]
            y_test = y[i]

            regr = linear_model.LinearRegression()
            regr.fit(X_train, y_train)
            regr_list.append(regr)
            diff.append(regr.predict(X_test)[0] / y_test)

        # find the best regr
        list_diff = list(abs(np.array(diff) - 1))
        best_regr_index = list_diff.index(min(list_diff))
        best_regr = regr_list[best_regr_index]

        print(list_diff[best_regr_index])
        print(y_pre)
        print(best_regr.predict(df_pre)[0])

        return best_regr

    def find_best_solution(self, best_regr_loans, best_regr_savings, goal_loans, goal_savings):
        m = Model("CIO")
        # set vars
        global_exp = m.addVar(vtype=GRB.INTEGER, name="Global_expenditure")
        saving_exp = m.addVar(vtype=GRB.INTEGER, name="Saving_expenditure")
        loan_exp = m.addVar(vtype=GRB.INTEGER, name="Loan_expenditure")
        # set objective
        m.setObjective(global_exp + saving_exp + loan_exp, GRB.MINIMIZE)
        # add constrs
        m.addConstr(global_exp * best_regr_loans.coef_[
                    0] + loan_exp * best_regr_loans.coef_[1] >= goal_loans, "loans_ta")
        m.addConstr(global_exp * best_regr_savings.coef_[
                    0] + saving_exp * best_regr_savings.coef_[1] >= goal_savings, "savings_ta")
        # fire!
        m.optimize()

        for v in m.getVars():
            print('%s: %g' % (v.varName, v.x))
        print('Obj: %g' % m.objVal)

    # source: https://datascience.stackexchange.com/questions/10459/calculation-and-visualization-of-correlation-matrix-with-pandas
    def correlation_matrix(self, df, title='CIO Correlation', xticks=4, colorbar_ticks=0.1):
        fig = plt.figure(figsize=(18, 16), dpi=160)
        ax1 = fig.add_subplot(111)
        cmap = cm.get_cmap('jet', 30)
        cax = ax1.imshow(df.corr(), interpolation="nearest", cmap=cmap)
        ax1.grid(True)
        plt.title(title)
        labels = list(df.columns)
        ax1.set_xticks(np.arange(0, len(labels), 4))
        ax1.set_yticks(np.arange(len(labels)))
        ax1.set_yticklabels(labels, fontsize=12)
        ax1.set_xticklabels(labels, fontsize=12)
        # Add colorbar, make sure to specify tick locations to match desired ticklabels
        fig.colorbar(cax, ticks=np.arange(-1.1, 1.1, 0.1))
        plt.show()
