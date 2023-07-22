from flask import Flask, render_template, request, jsonify
import csv
import folium
from MRT_BUS_WALK import PublicTransport as PT


app = Flask(__name__, static_folder='GUI/static', template_folder='GUI/templates')

@app.route('/')
def index():
    
    # Creating a Folium Map of Singapore
    m = folium.Map(location=[1.3521, 103.8198], zoom_start=12)
    # Render m
    m.get_root().render()

    map_sg = m.get_root()._repr_html_()
    return render_template('index.html', path=map_sg)

# Step 4: Handle the form submission and process the inputs
@app.route('/process', methods=['POST'])
def process():
    # Get the inputs from the form
    start = request.form['start']
    end = request.form['end']

    print(start, end)

    # Step 5: Call the Python script with the inputs and get the result
    path = PT.Route(start, end)

    # Return the result back to the HTML page
    return render_template('index.html', path=path)

# Endpoint to serve the new merged CSV data as JSON
@app.route('/get-merged-csv-data', methods=['GET'])
def get_merged_csv_data():
    with open('./Data/MRT Stations.csv', newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        data = [row for row in reader]
    return jsonify(data)



if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
