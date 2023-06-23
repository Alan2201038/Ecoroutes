import csv

def find(station_name, mrt_csv):
    with open(mrt_csv, 'r') as file:
        reader = csv.reader(file)

        for row in reader:
            if row[0] == station_name:
                latitude = row[2]
                longitude = row[3]
                return float(latitude), float(longitude)

    # Return None if station name is not found
    return None, None