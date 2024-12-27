import pandas as pd
import numpy as np
import sys

class File:
    def __init__(self, filename):
        self.filename = filename

    def get_file_name(self):
        return self.filename

class InFile(File):
    def __init__(self):
        fl_name = sys.argv[1]
        print(fl_name)
        super().__init__(fl_name)

    def get_dfr_from_file(self):
        dfr = pd.read_excel(self.filename)
        return dfr


class OutFile(File):
    def __init__(self, in_file_name, cat_name):
        out_file_name = in_file_name.replace(".xlsx", "_xlsx") + '__' + cat_name + '.xlsx'
        out_file_name = out_file_name.replace("/", "_")
        out_file_name = out_file_name.replace(" ", "_")
        super().__init__(out_file_name)

    def put_dfr_to_file(self, dfr):
        dfr.to_excel(self.filename, index=False)


class DataFrame:
    def __init__(self, dfr):
        self.data_frame = dfr

    def get_dataframe(self):
        return self.data_frame


class InDataFrame(DataFrame):
    def __init__(self, dfr_raw):
        dfr = dfr_raw.dropna(subset=['Input field', 'Value'])
        super().__init__(dfr)

    def get_category_list(self):
        category_list = list(self.data_frame['Case category'].drop_duplicates())
        return category_list


class OutDataFrame(DataFrame):
    def __init__(self, dfr, category):
        uniq_cat_dfr = dfr[dfr['Case category'] == category].copy(deep=True)
        uniq_cat_dfr.sort_values(by=["MSISDN", "Case ID", "Input field"], inplace=True)
        self.category_name = category
        super().__init__(uniq_cat_dfr)

    def get_category_name(self):
        return self.category_name

    def modify_dfr(self):
        dfr_begin = self.data_frame.drop(labels=['Input field', 'Value'], axis="columns").copy(deep=True)
        dfr_begin.drop_duplicates(subset=["MSISDN", "Case ID"], inplace=True)
        case_ids = dfr_begin['Case ID'].values.tolist()

        dfr_end = pd.concat([self.data_frame['Case ID'], self.data_frame['Input field'], self.data_frame['Value']], axis=1)
        dfr_end.set_index(keys="Case ID", inplace=True)
        columns_mod = dfr_end.loc[case_ids[0]]["Input field"].values
        lst_mod_ends = []
        for i in range(0, len(case_ids)):
            lst_mod_ends.append(dfr_end.loc[case_ids[i]]["Value"].values)
        dfr_ends_mod = pd.DataFrame(columns=columns_mod, data=lst_mod_ends)

        dfr_begin.reset_index(inplace=True)
        self.data_frame = pd.concat(objs=[dfr_begin, dfr_ends_mod], axis=1)

        return 0


def main():
    in_file = InFile()
    in_dfr = InDataFrame(in_file.get_dfr_from_file())
    print(in_dfr.get_dataframe())
    category_list = in_dfr.get_category_list()
    print("\n", category_list)
    out_dfr_list = []
    out_file_lst = []
    out_dfr_pointer = 0
    print("\n========================================================================================\n")
    for category in category_list:
        print(category, "\n")
        out_dfr_list.append(OutDataFrame(in_dfr.get_dataframe(), category))
        print(out_dfr_list[out_dfr_pointer].get_dataframe())
        mod_flag = out_dfr_list[out_dfr_pointer].modify_dfr()
        if mod_flag == 0:
            print("\n\n", out_dfr_list[out_dfr_pointer].get_dataframe())
            out_file_lst.append(OutFile(in_file.get_file_name(), category))
        out_dfr_pointer += 1

    print("\n========================================================================================\n")
    out_dfr_pointer = 0
    for ou_file in out_file_lst:
        print(ou_file.get_file_name())
        ou_file.put_dfr_to_file(out_dfr_list[out_dfr_pointer].get_dataframe())
        out_dfr_pointer += 1


if __name__ == "__main__":
    main()
