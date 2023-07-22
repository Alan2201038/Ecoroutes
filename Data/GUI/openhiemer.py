import pandas as pd

def merge_columns_and_add(csv_file_path):
    # Read the CSV file into a pandas DataFrame
    df = pd.read_csv(csv_file_path, header=None)

    # Merge the first two columns into a new column
    df['Merged_Column'] = df[0].astype(str) + ' ' + df[1].astype(str)

    # Save the DataFrame back to the CSV file
    df.to_csv(csv_file_path, index=False, header=False)

if __name__ == "__main__":
    # Replace 'your_file.csv' with the actual path to your CSV file
    file_path = 'bus_stops.csv'

    # Call the function to merge columns and add the new merged column to the CSV
    merge_columns_and_add(file_path)