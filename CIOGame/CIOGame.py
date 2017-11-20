import csv
import numpy as np
import pandas as pd
from matplotlib import pyplot as plt
from matplotlib import cm as cm

class CIOGame:
    def __init__(self,lines, periods=0):
        for period in range(periods+1):
            for report_name in lines:
                report_reader = csv.reader(open("Reports/%s/%s"%(period,report_name), newline='\n'), delimiter=',')
                for index, row in enumerate(report_reader):
                    if index in lines[report_name]:
                        content_name=self.get_content_name(row)
                        if hasattr(self, content_name):
                            getattr(self,content_name).append(self.formate_content(row))
                        else:
                            setattr(self,content_name,[self.formate_content(row)])
        
    def formate_content(self, row_list):
        content_position=2 if row_list[1]=="" else 1
        contents=row_list[content_position].split(" ")
        content_value=float(contents[0].replace(".","").replace(",","."))
        # if with "%","TA/yr"...
        if len(contents)>1:
            if contents[1]=="%":
                content_value/=100
        return content_value

    def get_content_name(self, row_list):
        return row_list[0].replace(" -","").replace("&","").replace(".","").replace(" ","_")

    #source: https://datascience.stackexchange.com/questions/10459/calculation-and-visualization-of-correlation-matrix-with-pandas
    def correlation_matrix(self,df,title='CIO Correlation',xticks=4,colorbar_ticks=0.1):
        fig = plt.figure(figsize=(18, 16),dpi=160)
        ax1 = fig.add_subplot(111)
        cmap = cm.get_cmap('jet', 30)
        cax = ax1.imshow(df.corr(), interpolation="nearest", cmap=cmap)
        ax1.grid(True)
        plt.title(title)
        labels=list(df.columns)
        ax1.set_xticks(np.arange(0,len(labels),4))
        ax1.set_yticks(np.arange(len(labels)))
        ax1.set_yticklabels(labels,fontsize=12)
        ax1.set_xticklabels(labels,fontsize=12)
        # Add colorbar, make sure to specify tick locations to match desired ticklabels
        fig.colorbar(cax, ticks=np.arange(-1.1, 1.1, 0.1))
        plt.show()
