#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Sep 25 22:48:47 2024

@author: enzorodriguez
"""

from flask_cors import CORS
from flask import Flask, request, jsonify
import pandas as pd
from fuzzywuzzy import fuzz, process
import logging  # Import logging module

# Configure logging
logging.basicConfig(level=logging.INFO)

# Load the dataset
file_path = './Updated_FinancialInclusion_Final.csv'
data = pd.read_csv(file_path)

cities_list = data['Cities'].str.lower().unique()
provinces_list = data['Province'].str.lower().unique()

# Create Flask app
app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

# Fuzzy matching functions
def get_fis_in_city(city_name, df):
    city_name = city_name.strip().lower()
    df['Cities'] = df['Cities'].str.strip().str.lower()

    # Lower the threshold slightly for better matching
    result = process.extractOne(city_name, df['Cities'], scorer=fuzz.partial_ratio)
    
    if result:
        closest_match, score = result[0], result[1]
        if score >= 80:  # Adjusted matching threshold
            city_data = df[df['Cities'] == closest_match]
            return city_data[['Cities', 'Province', 'Total Number of Fis']].to_dict(orient='records')
    
    return f"No data found for city: {city_name}"

def get_cities_in_province(province_name, df):
    province_name = province_name.strip().lower()
    df['Province'] = df['Province'].str.strip().str.lower()
    result = process.extractOne(province_name, df['Province'], scorer=fuzz.partial_ratio)
    
    if result:
        closest_match, score = result[0], result[1]
        if score >= 90:
            province_data = df[df['Province'] == closest_match]
            cities_info = province_data[['Cities', 'Total Number of Fis']].to_dict(orient='records')
            total_fis_in_province = province_data['Total Number of Fis'].sum()
            city_with_highest_fis = province_data.loc[province_data['Total Number of Fis'].idxmax()]
            city_with_lowest_fis = province_data.loc[province_data['Total Number of Fis'].idxmin()]
            response = {
                'Province': closest_match,
                'Total FIs in Province': total_fis_in_province,
                'Cities and FIs': cities_info,
                'City with Highest FIs': {
                    'City': city_with_highest_fis['Cities'],
                    'Total FIs': city_with_highest_fis['Total Number of Fis']
                },
                'City with Lowest FIs': {
                    'City': city_with_lowest_fis['Cities'],
                    'Total FIs': city_with_lowest_fis['Total Number of Fis']
                }
            }
            return response
    return f"No data found for province: {province_name}"

# Example function to detect city or province (ensure this is defined)
def detect_city_or_province(user_input, cities_list, provinces_list):
    user_input = user_input.lower()

    closest_city = process.extractOne(user_input, cities_list, scorer=fuzz.partial_ratio)
    if closest_city and closest_city[1] >= 90:
        return 'city', closest_city[0]

    closest_province = process.extractOne(user_input, provinces_list, scorer=fuzz.partial_ratio)
    if closest_province and closest_province[1] >= 90:
        return 'province', closest_province[0]

    return None, None

# Flask route to interact with the chatbot
@app.route('/chatbot', methods=['GET', 'POST'])
def chatbot():
    try:
        if request.method == 'GET':
            return "Chatbot is running. Please use POST requests."
        
        user_input = request.json.get('query', '').lower()
        logging.info(f"User input: {user_input}")

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
            response = "I don't understand your query. Please ask about cities, provinces, or statistics."
        
        logging.info(f"Response: {response}")
        return jsonify(response)
    
    except Exception as e:
        logging.error(f"Error: {e}")
        return jsonify({"error": "Internal server error"}), 500

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)
