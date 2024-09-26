from flask import Flask, request, render_template
import pandas as pd
from fuzzywuzzy import fuzz
from fuzzywuzzy import process

app = Flask(__name__)

# Load the dataset
file_path = 'Updated_FinancialInclusion_Final.csv'
data = pd.read_csv(file_path)

# Prepare city and province lists for matching
cities_list = data['Cities'].str.lower().unique()
provinces_list = data['Province'].str.lower().unique()

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

# Functions for fuzzy matching and getting financial institution data remain the same as in your current code

if __name__ == '__main__':
    import os
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
    # Trigger redeployment