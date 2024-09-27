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

# Global variable to store the user's current search context (city/province/statistics)
user_context = {
    'type': None,  # 'city', 'province', 'statistics'
    'awaiting_input': False  # Whether the bot is waiting for the user to answer a question
}

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
        cities_info = province_data[['Cities', 'Total Number of Fis']].to_dict(orient='records')
        total_fis = province_data['Total Number of Fis'].sum()
        max_fis = province_data.loc[province_data['Total Number of Fis'].idxmax()]
        min_fis = province_data.loc[province_data['Total Number of Fis'].idxmin()]
        return {
            'Province': closest_match,
            'Total FIs': total_fis,
            'Cities and FIs': cities_info,
            'City with Max FIs': f"{max_fis['Cities']} ({max_fis['Total Number of Fis']} FIs)",
            'City with Min FIs': f"{min_fis['Cities']} ({min_fis['Total Number of Fis']} FIs)"
        }
    
    return f"No data found for province: {province_name}"

def get_average_fis(df):
    average_fis = df['Total Number of Fis'].mean()
    return f"The average number of FIs across all locations is {average_fis:.2f} FIs."

# Chatbot route
@app.route('/chatbot', methods=['POST'])
def chatbot():
    user_input = request.json.get('query', '').lower()

    if user_input == 'exit':
        return jsonify("Thank you for using the chatbot! Goodbye.")

    # Continue with city, province, or statistics detection and switching logic
    global current_mode
    if current_mode is None:  # First question or after reset
        current_mode = "ask_category"
        return jsonify("Are you asking about a city, a province, or statistics?")

    if current_mode == "ask_category":
        if "city" in user_input:
            current_mode = "city"
            return jsonify("Please provide the name of the city.")
        elif "province" in user_input:
            current_mode = "province"
            return jsonify("Please provide the name of the province.")
        elif "statistics" in user_input:
            current_mode = "statistics"
            return jsonify("Please specify 'mean', 'max', or 'min'.")
        else:
            return jsonify("Please choose from 'city', 'province', or 'statistics'.")

    if current_mode == "city":
        response = get_fis_in_city(user_input, data)
        if response:
            current_mode = "ask_next_step"
            return jsonify(f"{response}, Do you want to continue searching for cities, or switch to provinces or statistics?")
        else:
            return jsonify("No data found for city: " + user_input)

    if current_mode == "province":
        response = get_cities_in_province(user_input, data)
        if response:
            current_mode = "ask_next_step"
            return jsonify(f"{response}, Do you want to continue searching for provinces, or switch to cities or statistics?")
        else:
            return jsonify("No data found for province: " + user_input)

    if current_mode == "statistics":
        response = handle_statistics_query(user_input, data)
        if response:
            current_mode = "ask_next_step"
            return jsonify(f"{response}, Do you want to continue searching for statistics, or switch to cities or provinces?")
        else:
            return jsonify("Statistics type not recognized. Please ask for 'mean', 'max', or 'min'.")

    if current_mode == "ask_next_step":
        if "continue" in user_input:
            if "city" in last_query_type:
                return jsonify("Please provide the name of the city.")
            elif "province" in last_query_type:
                return jsonify("Please provide the name of the province.")
        elif "switch" in user_input:
            current_mode = "ask_category"
            return jsonify("Are you asking about a city, a province, or statistics?")
        else:
            return jsonify("Please respond with 'continue' to keep searching or 'switch' to change categories.")

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)
