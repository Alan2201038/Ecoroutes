from flask import Flask, render_template, request, jsonify


app = Flask(__name__, static_folder='GUI/static', template_folder='GUI/templates')

@app.route('/')
def index():
    return render_template('index.html')

# Step 4: Handle the form submission and process the inputs
@app.route('/process', methods=['POST'])
def process():
    # Get the inputs from the form
    start = request.form['start']
    end = request.form['end']

    print(start, end)

    # Step 5: Call the Python script with the inputs and get the result
    path = GUI.Mrt_Route(start, end)

    # Return the result back to the HTML page
    return render_template('index.html', path=path)

# Define your Google Maps API key
google_maps_api_key = "AIzaSyALi-eGCrt1wQkiO5ZeXHaWrHxHdTUpzX"

@app.route("/eco")
def eco():
    return render_template("map.html", google_maps_api_key=google_maps_api_key)

@app.route("/search", methods=["POST"])
def search():
    query = request.form["query"]

    # Use the Google Places API Places Autocomplete to get place details
    url = f"https://maps.googleapis.com/maps/api/place/autocomplete/json"
    params = {
        "input": query,
        "types": "geocode",
        "key": google_maps_api_key
    }
    response = request.get(url, params=params)
    data = response.json()

    if data["status"] == "OK" and data.get("predictions"):
        place_id = data["predictions"][0]["place_id"]

        # Use the Google Places API Place Details to get latitude and longitude
        url = f"https://maps.googleapis.com/maps/api/place/details/json"
        params = {
            "place_id": place_id,
            "fields": "geometry",
            "key": google_maps_api_key
        }
        response = request.get(url, params=params)
        data = response.json()

        if data["status"] == "OK":
            location = data["result"]["geometry"]["location"]
            lat = location["lat"]
            lng = location["lng"]

            # Use Folium to create and display the map with a marker
            # Import folium and create the map, add a marker at (lat, lng)
            # folium_map = ...

            # Return the map HTML or send it to the template
            return "<h1>Map with marker will be displayed here</h1>"

    return "Error: Location not found."



if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)

# API KEY = AIzaSyALi-eGCrt1wQkiO5ZeXHaWrHxHdTUpzXU
# <script async
#     src="https://maps.googleapis.com/maps/api/js?key=AIzaSyALi-eGCrt1wQkiO5ZeXHaWrHxHdTUpzX&libraries=places&callback=initMap">
# </script>