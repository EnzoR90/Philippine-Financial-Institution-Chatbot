from flask import Flask, request, render_template
import pandas as pd
from fuzzywuzzy import fuzz
from fuzzywuzzy import process
from whitenoise import WhiteNoise
app = Flask(__name__, static_folder='static', static_url_path='/static')
app.wsgi_app = WhiteNoise(app.wsgi_app, root='static/')

# Load the dataset
file_path = 'Updated_FinancialInclusion_Final.csv'
data = pd.read_csv(file_path)

# Prepare city and province lists for matching
cities_list = data['Cities'].str.lower().unique()
provinces_list = data['Province'].str.lower().unique()

@app.route('/hello')
def hello():
    return "Hello, World!"

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/get_response', methods=['POST'])
def get_response():
    user_input = request.form['user_input'].lower()

    # Detect city or province in the user input
    entity_type, entity_value = detect_city_or_province(user_input, cities_list, provinces_list)

    if entity_type == 'city':
        response = get_fis_in_city(entity_value, data)
    elif entity_type == 'province':
        response = get_cities_in_province(entity_value, data)
    elif "highest" in user_input or "most" in user_input:
        response = get_city_with_extreme_fis(data, highest=True)
    elif "lowest" in user_input or "fewest" in user_input:
        response = get_city_with_extreme_fis(data, highest=False)
    elif "average" in user_input or "statistics" in user_input:
        response = get_average_fis(data)
    else:
        response = "I'm sorry, I don't understand your query. Please ask about cities, provinces, or statistics."

    return render_template('response.html', response=response)

# Function to detect city or province
def detect_city_or_province(user_input, cities_list, provinces_list):
    # Fuzzy match city with a higher threshold of 90 for more precise matches
    closest_city = process.extractOne(user_input, cities_list, scorer=fuzz.partial_ratio)
    if closest_city and closest_city[1] >= 90:
        return 'city', closest_city[0]

    # Fuzzy match province with a threshold of 90 for more accurate matches
    closest_province = process.extractOne(user_input, provinces_list, scorer=fuzz.partial_ratio)
    if closest_province and closest_province[1] >= 90:
        return 'province', closest_province[0]

    return None, None

# Run the Flask app
if __name__ == '__main__':
    import os
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)