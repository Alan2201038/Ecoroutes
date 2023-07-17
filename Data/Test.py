import csv

def read_csv_column(filename, column_index):
    data = []
    with open(filename, newline='') as csvfile:
        reader = csv.reader(csvfile)
        for row in reader:
            if len(row) >= column_index + 1:
                data.append(row[column_index])
    return data

def check_strings_in_another_csv(file1, file2):
    column1_file1 = read_csv_column(file1, 0)
    column2_file2 = read_csv_column(file2, 1)

    for string_to_check in column1_file1:
        matched_strings = [item for item in column2_file2 if string_to_check.lower() in item.lower()]
        
        if matched_strings:
            # print(f"String '{string_to_check}' from column 1 in '{file1}' is present in column 2 of '{file2}'.")
            # print(f"Items in '{file2}' that matched: {', '.join(matched_strings)}")
            print("ok")
        else:
            print(f"String '{string_to_check}' from column 1 in '{file1}' is NOT present in column 2 of '{file2}'.")

if __name__ == "__main__":
    file1_path = "data/mrt_time_test.csv"
    file2_path = "data/mrtsg.csv"
    check_strings_in_another_csv(file1_path, file2_path)
