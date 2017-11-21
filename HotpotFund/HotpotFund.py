import pandas as pd
import time
import os


class HotpotFund:
    def __init__(self, benchmark_path="benchmark/", csv_delimiter=",", record_name="record.csv", label_name="label.csv"):
        self.record_name = record_name
        self.label_name = label_name
        self.benchmark_path = benchmark_path
        records = self.read_file(
            benchmark_path, record_name, csv_delimiter)
        labels = self.read_file(
            benchmark_path, label_name, csv_delimiter)
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
            print("creating file %s" % (file_name))
            # create a new file to store contents
            header = ""
            if file_name == "record.csv":
                header = "start,stop,index\n"
            elif file_name == "label.csv":
                header = "index,parent_index,name,display\n"
            write_file(file_path, header)
            print("created file %s" % (file_name))
            return pd.DataFrame(None)

    def get_labels(self):
        labels_string_list = []
        for index, label in self.labels.items():
            if label.parent != None:
                labels_string_list.append(
                    ":".join([str(index), label.name, label.parent.name]))
            else:
                labels_string_list.append(":".join([str(index), label.name]))
        return labels_string_list

    def creat_new_label(self, index):
        name = input("Type the name of label ")
        parent_index = int(input("Type the parent index of label "))
        while parent_index not in self.labels.keys() and parent_index != index:
            parent_index = int(input("Type the parent index of label "))
        new_label = Label(
            index, name, None if parent_index == index else self.labels[parent_index])
        self.labels[index] = new_label
        self.write_file(self.benchmark_path + self.label_name,
                        ",".join([str(index), str(parent_index), name]) + "\n")

    def start_fund(self):
        selected_label_index = int(input(
            "Select the index:\n" + '\n'.join(self.get_labels()) + "\n"))
        if selected_label_index not in self.labels.keys():
            self.creat_new_label(selected_label_index)
        self.selected_label_index = selected_label_index
        self.start_time = time.time()
        self.stop_time = time.time()

    def stop_fund(self):
        self.stop_time = time.time()
        self.write_file(self.benchmark_path + self.record_name,
                        ",".join([str(self.start_time), str(self.stop_time), str(self.selected_label_index)]) + "\n")
        print("Spend %s on %s" % (time.strftime("%H:%M:%S",
                                                time.gmtime(self.stop_time - self.start_time)), self.labels[self.selected_label_index].name))

    def write_file(self, file_path, csv_lines):
        if os.path.exists(file_path):
            append_write = 'a'  # append if already exists
        else:
            append_write = 'w'  # make a new file if not
        file = open(file_path, append_write)
        if isinstance(csv_lines, list):
            for csv_line in csv_lines:
                file.write(csv_line)
        else:
            file.write(csv_lines)
            # print(csv_lines)
        file.close()


class Label:
    def __init__(self, index, name, parent):
        self.index = index
        self.name = name
        self.parent = parent
