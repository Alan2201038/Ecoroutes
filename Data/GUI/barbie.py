import csv
import pandas as pd

input_csv_file = 'bus_stops.csv'
output_csv_file = 'bus_stops.csv'
column_to_delete = 'Location'

df = pd.read_csv(input_csv_file)
df.drop(column_to_delete, axis=1, inplace=True)
df.to_csv(output_csv_file, index=False)
