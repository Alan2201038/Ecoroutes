from flask import Flask, render_template, request, jsonify
import csv
import folium
from MRT_BUS_WALK import PublicTransport as PT
from Cars import CarOnly as Car


app = Flask(__name__, static_folder='GUI/static', template_folder='GUI/templates')

@app.route('/')
def index():
    
    # Creating a Folium Map of Singapore
    m = folium.Map(location=[1.3521, 103.8198], zoom_start=12)
    # Render m
    m.get_root().render()

    map_sg = m.get_root()._repr_html_()
    return render_template('index.html', path=map_sg)

# Function to format the string if it contains numbers
def format_string(s):
    if any(char.isdigit() for char in s):
        return "Bus Stop " + s
    return s

# Step 4: Handle the form submission and process the inputs
@app.route('/process', methods=['POST'])
def process():
    # Get the inputs from the form
    start = request.form['start']
    end = request.form['end']
    transport = request.form['transport']

    # print(start, end_location, transport)
    start_location = format_string(start)
    end_location = format_string(end)

    print(start_location, end_location)

    # Step 5: Call the Python script with the inputs and get the result
    if transport == 'PT':
        mode = request.form['mode']

        time_taken, carbon_emission, path = PT.Route(start, end, mode)

        print(time_taken, carbon_emission)

    elif transport == 'Car':
        if 'STATION' in start:
            # Read data from the first CSV file and add its first column to the merged list
            with open('./Data/GUI/MRT Stations.csv', newline='') as csvfile:
                reader = csv.reader(csvfile)
                for row in reader:
                    if start in row[0]:  # Check if the row is not empty
                        start_coordinates = (float(row[2]), float(row[3]))
        else:
            # Read data from the second CSV file
            with open('./Data/GUI/bus_stops.csv', newline='') as csvfile:
                reader = csv.reader(csvfile)
                for row in reader:
                    if start in row[0]:  # Check if the row is not empty
                        start_coordinates = (float(row[2]), float(row[3]))

        if 'STATION' in end:
            # Read data from the first CSV file and add its first column to the merged list
            with open('./Data/GUI/MRT Stations.csv', newline='') as csvfile:
                reader = csv.reader(csvfile)
                for row in reader:
                    if end in row[0]:  # Check if the row is not empty
                        end_coordinates = (float(row[2]), float(row[3]))
        else:
            # Read data from the second CSV file
            with open('./Data/GUI/bus_stops.csv', newline='') as csvfile:
                reader = csv.reader(csvfile)
                for row in reader:
                    if end in row[0]:  # Check if the row is not empty
                        end_coordinates = (float(row[2]), float(row[3]))

        time_taken, carbon_emission, path = Car.Route(start_coordinates, end_coordinates)

        print(time_taken, carbon_emission)

        
    # print(path)

    # Return the result back to the HTML page
    return render_template('index.html', path=path, time_taken=time_taken,carbon_emission=carbon_emission, start_location=start_location, end_location=end_location)
    # return jsonify({'path' : path})

# Endpoint to serve the new merged CSV data as JSON
@app.route('/get-merged-csv-data', methods=['GET'])
def get_merged_csv_data():
    # List to store the merged data from both CSV files
    merged_data = []

    # Read data from the first CSV file and add its first column to the merged list
    with open('./Data/GUI/MRT Stations.csv', newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            if row:  # Check if the row is not empty
                merged_data.append(row)

    with open('./Data/GUI/bus_stops.csv', newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            if row:  # Check if the row is not empty
                merged_data.append(row)

    return jsonify(merged_data)

@app.route('/get-mrt-data', methods=['GET'])
def get_mrt_data():
    # Read data from the first CSV file
    with open('./Data/GUI/MRT Stations.csv', newline='') as csvfile:
        mrt_reader = csv.DictReader(csvfile)
        mrt_data = [row for row in mrt_reader]

    # Return the MRT data as a JSON response
    return jsonify(mrt_data)

@app.route('/get-bus-data', methods=['GET'])
def get_bus_data():
    # Read data from the second CSV file
    with open('./Data/GUI/bus_stops.csv', newline='') as csvfile:
        bus_reader = csv.DictReader(csvfile)
        bus_data = [row for row in bus_reader]

    # Return the bus data as a JSON response
    return jsonify(bus_data)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
