from flask import Flask, render_template, request, jsonify
from MRTs import MRT_GUI as GUI

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


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)