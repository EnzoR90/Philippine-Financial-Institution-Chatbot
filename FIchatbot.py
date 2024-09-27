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

# Load the dataset
file_path = './Updated_FinancialInclusion_Final.csv'
data = pd.read_csv(file_path)

cities_list = data['Cities'].str.lower().unique()
provinces_list = data['Province'].str.lower().unique()

# Create Flask app
app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

# Global variable to store the chatbot state
current_mode = None
last_query_type = None  # Tracks whether last query was city/province/statistics

# Fuzzy matching functions
def get_fis_in_city(city_name, df):
    city_name = city_name.strip().lower()
    df['Cities'] = df['Cities'].str.strip().str.lower()
    result = process.extractOne(city_name, df['Cities'], scorer=fuzz.partial_ratio)

    if result and result[1] >= 80:
        closest_match = result[0]
        city_data = df[df['Cities'] == closest_match]
        return f"{city_data.iloc[0]['Cities']}, {city_data.iloc[0]['Province']}: {city_data.iloc[0]['Total Number of Fis']} FIs"

    return f"No data found for city: {city_name}"

def get_cities_in_province(province_name, df):
    province_name = province_name.strip().lower()
    df['Province'] = df['Province'].str.strip().str.lower()
    result = process.extractOne(province_name, df['Province'], scorer=fuzz.partial_ratio)

    if result and result[1] >= 80:
        closest_match = result[0]
        province_data = df[df['Province'] == closest_match]
        total_fis = province_data['Total Number of Fis'].sum()
        max_fis = province_data.loc[province_data['Total Number of Fis'].idxmax()]
        min_fis = province_data.loc[province_data['Total Number of Fis'].idxmin()]
        return f"{closest_match} has {total_fis} FIs. Highest FIs: {max_fis['Cities']} ({max_fis['Total Number of Fis']} FIs). Lowest FIs: {min_fis['Cities']} ({min_fis['Total Number of Fis']} FIs)."
    
    return f"No data found for province: {province_name}"

def handle_statistics_query(stat_type, df):
    if stat_type == "mean":
        avg_fis = df['Total Number of Fis'].mean()
        return f"The average number of FIs is {avg_fis:.2f}."
    elif stat_type == "max":
        max_city = df.loc[df['Total Number of Fis'].idxmax()]
        return f"The city with the most FIs is {max_city['Cities']} with {max_city['Total Number of Fis']} FIs."
    elif stat_type == "min":
        min_city = df.loc[df['Total Number of Fis'].idxmin()]
        return f"The city with the fewest FIs is {min_city['Cities']} with {min_city['Total Number of Fis']} FIs."
    return "Statistics type not recognized. Please ask for 'mean', 'max', or 'min'."

# Chatbot route
@app.route('/chatbot', methods=['POST'])
def chatbot():
    user_input = request.json.get('query', '').lower()

    if user_input == 'exit':
        return jsonify("Thank you for using the chatbot! Goodbye.")

    # Continue with city, province, or statistics detection and switching logic
    global current_mode, last_query_type

    if current_mode is None:  # First question or after reset
        current_mode = "ask_category"
        return jsonify("Are you asking about a city, a province, or statistics?")

    if current_mode == "ask_category":
        if "city" in user_input:
            current_mode = "city"
            last_query_type = "city"
            return jsonify("Please provide the name of the city.")
        elif "province" in user_input:
            current_mode = "province"
            last_query_type = "province"
            return jsonify("Please provide the name of the province.")
        elif "statistics" in user_input:
            current_mode = "statistics"
            last_query_type = "statistics"
            return jsonify("Please specify 'mean', 'max', or 'min'.")
        else:
            return jsonify("Please choose from 'city', 'province', or 'statistics'.")

    if current_mode == "city":
        response = get_fis_in_city(user_input, data)
        current_mode = "ask_next_step"
        return jsonify(f"{response}. Do you want to continue searching for cities, or switch to provinces or statistics?")

    if current_mode == "province":
        response = get_cities_in_province(user_input, data)
        current_mode = "ask_next_step"
        return jsonify(f"{response}. Do you want to continue searching for provinces, or switch to cities or statistics?")

    if current_mode == "statistics":
        response = handle_statistics_query(user_input, data)
        current_mode = "ask_next_step"
        return jsonify(f"{response}. Do you want to continue searching for statistics, or switch to cities or provinces?")

    if current_mode == "ask_next_step":
        if "continue" in user_input:
            current_mode = last_query_type  # Go back to the last query type (city/province/statistics)
            if last_query_type == "city":
                return jsonify("Please provide the name of the city.")
            elif last_query_type == "province":
                return jsonify("Please provide the name of the province.")
            elif last_query_type == "statistics":
                return jsonify("Please specify 'mean', 'max', or 'min'.")
        elif "switch" in user_input:
            current_mode = "ask_category"
            return jsonify("Are you asking about a city, a province, or statistics?")
        else:
            return jsonify("Please respond with 'continue' to keep searching or 'switch' to change categories.")

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)
