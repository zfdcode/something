import pandas as pd
import time


class HotpotFund:
    def __init__(self, benchmark_path="benchmark/", csv_delimiter=","):
        records = self.read_file(
            benchmark_path, "record.csv", csv_delimiter)
        labels = self.read_file(
            benchmark_path, "label.csv", csv_delimiter)
        self.records = self.read_records(records)
        self.labels = self.read_labels(labels)

    def read_records(self, record_df):
        records = {}
        if not record_df.empty:
            records = record_df

    def read_labels(self, labels_df):
        labels = {}
        # label_info=[index,parent_index,name]
        if not labels_df.empty:
            for label_info in labels_df.values:
                # if is a parent node
                if label_info[0] == label_info[1]:
                    labels[label_info[0]] = Label(
                        label_info[0], label_info[2], None)
                else:
                    labels[label_info[0]] = Label(
                        label_info[0], label_info[2], labels[label_info[1]])
        return labels

    def read_file(self, benchmark_path, file_name, csv_delimiter):
        file_path = benchmark_path + file_name
        try:
            file_df = pd.read_csv(file_path, sep=csv_delimiter)
            return file_df
        except IOError:
            print("no such file " + file_path)
            return pd.DataFrame(None)

    def get_labels(self):
        labels_string_list = []
        for index, label in self.labels.items():
            if label.parent != None:
                labels_string_list.append(":".join([str(index), label.name]))
        return labels_string_list

    def creat_new_label(self, index):
        name = input("Type the name of label")
        parent_index = int(input("Type the parent index of label\n"))
        while parent_index not in self.labels.keys() and parent_index != index:
            parent_index = int(input("Type the parent index of label\n"))
        self.labels[index] = Label(
            index, name, None if parent_index == index else self.labels[parent_index])

    def start_fund(self):
        selected_label_index = input(
            "Select the index:\n" + '\n'.join(self.get_labels()) + "\n")
        if int(selected_label_index) not in self.labels.keys():
            self.creat_new_label(selected_label_index)
        self.start_time = time.time()
        self.stop_time = time.time()


class Label:
    def __init__(self, index, name, parent):
        self.index = index
        self.name = name
        self.parent = parent
