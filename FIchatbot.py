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
import logging

# Set up logging
logging.basicConfig(level=logging.DEBUG)

# Load the dataset
file_path = './Updated_FinancialInclusion_Final.csv'
data = pd.read_csv(file_path)

cities_list = data['Cities'].str.lower().unique()
provinces_list = data['Province'].str.lower().unique()

# Create Flask app
app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

# Improved Fuzzy matching for cities
def get_fis_in_city(city_name, df):
    logging.debug(f"Searching for city: {city_name}")
    city_name = city_name.strip().lower()
    df['Cities'] = df['Cities'].str.strip().str.lower()

    # Loosen the fuzzy matching threshold slightly
    result = process.extractOne(city_name, df['Cities'], scorer=fuzz.partial_ratio)
    
    if result:
        closest_match, score = result[0], result[1]
        logging.debug(f"Best match: {closest_match} with score: {score}")
        if score >= 80:  # Loosened matching threshold
            city_data = df[df['Cities'] == closest_match]
            return city_data[['Cities', 'Province', 'Total Number of Fis']].to_dict(orient='records')
    
    return f"No data found for city: {city_name}"

# Fuzzy matching for provinces
def get_cities_in_province(province_name, df):
    logging.debug(f"Searching for province: {province_name}")
    province_name = province_name.strip().lower()
    df['Province'] = df['Province'].str.strip().str.lower()

    # Fuzzy match the province
    result = process.extractOne(province_name, df['Province'], scorer=fuzz.partial_ratio)
    
    if result:
        closest_match, score = result[0], result[1]
        logging.debug(f"Best match: {closest_match} with score: {score}")
        if score >= 90:  # Stricter matching threshold for provinces
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

# Improved handling of query detection
def detect_query_type(user_input, cities_list, provinces_list):
    logging.debug(f"Processing user input: {user_input}")
    user_input = user_input.lower().strip()

    # Handle the 'exit' command explicitly
    if "exit" in user_input:
        return 'exit', None

    # Strip extra words like "city", "province", etc.
    stripped_input = user_input.replace("city", "").replace("province", "").strip()

    # Check if the query contains a statistic keyword
    if any(stat in stripped_input for stat in ["mean", "average", "max", "highest", "min", "lowest"]):
        return 'statistic', stripped_input
    
    # Fuzzy match for cities
    closest_city = process.extractOne(stripped_input, cities_list, scorer=fuzz.partial_ratio)
    if closest_city and closest_city[1] >= 80:
        logging.debug(f"City detected: {closest_city[0]} with score: {closest_city[1]}")
        return 'city', closest_city[0]

    # Fuzzy match for provinces
    closest_province = process.extractOne(stripped_input, provinces_list, scorer=fuzz.partial_ratio)
    if closest_province and closest_province[1] >= 90:
        logging.debug(f"Province detected: {closest_province[0]} with score: {closest_province[1]}")
        return 'province', closest_province[0]

    return None, None

# Flask route to interact with the chatbot
@app.route('/chatbot', methods=['GET', 'POST'])
def chatbot():
    if request.method == 'GET':
        return "Chatbot is running. Please use POST requests."
    
    user_input = request.json.get('query', '').lower()
    query_type, query_value = detect_query_type(user_input, cities_list, provinces_list)

    # Handle 'exit' query
    if query_type == 'exit':
        return jsonify("Thank you for using the chatbot! Goodbye.")

    if query_type == 'city':
        response = get_fis_in_city(query_value, data)
    elif query_type == 'province':
        response = get_cities_in_province(query_value, data)
    elif query_type == 'statistic':
        response = get_statistics(data, query_value)
    else:
        response = "I don't understand your query. Please ask about cities, provinces, or statistics."

    return jsonify(response)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)
