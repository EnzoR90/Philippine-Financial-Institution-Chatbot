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

# Global variable to track query type (city, province, or statistics)
session_state = {
    "query_type": None  # Keeps track of whether the user is asking about city, province, or statistics
}

# Fuzzy matching functions
def get_fis_in_city(city_name, df):
    logging.debug(f"Searching for city: {city_name}")
    city_name = city_name.strip().lower()
    df['Cities'] = df['Cities'].str.strip().str.lower()

    result = process.extractOne(city_name, df['Cities'], scorer=fuzz.partial_ratio)
    
    if result:
        closest_match, score = result[0], result[1]
        logging.debug(f"Best match: {closest_match} with score: {score}")
        if score >= 80:
            city_data = df[df['Cities'] == closest_match]
            return city_data[['Cities', 'Province', 'Total Number of Fis']].to_dict(orient='records')
    
    return f"No data found for city: {city_name}"

def get_cities_in_province(province_name, df):
    logging.debug(f"Searching for province: {province_name}")
    province_name = province_name.strip().lower()
    df['Province'] = df['Province'].str.strip().str.lower()

    result = process.extractOne(province_name, df['Province'], scorer=fuzz.partial_ratio)
    
    if result:
        closest_match, score = result[0], result[1]
        logging.debug(f"Best match: {closest_match} with score: {score}")
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

# Detect query type (city, province, or statistics)
def detect_query_type(user_input):
    if "city" in user_input:
        session_state["query_type"] = "city"
        return "Please provide the name of the city."
    elif "province" in user_input:
        session_state["query_type"] = "province"
        return "Please provide the name of the province."
    elif any(stat in user_input for stat in ["mean", "average", "max", "highest", "min", "lowest"]):
        session_state["query_type"] = "statistics"
        return "Please specify the type of statistic (mean, max, min)."
    else:
        return "Are you asking about a city, a province, or statistics?"

# Reset session state after completion of a query
def reset_session():
    session_state["query_type"] = None

# Follow-up question to continue or switch
def follow_up_question():
    return "Do you want to continue searching for cities, or do you want to switch to provinces or statistics?"

# Flask route to interact with the chatbot
@app.route('/chatbot', methods=['GET', 'POST'])
def chatbot():
    if request.method == 'GET':
        return "Chatbot is running. Please use POST requests."
    
    user_input = request.json.get('query', '').lower()

    # Exit condition
    if "exit" in user_input:
        reset_session()
        return jsonify("Thank you for using the chatbot! Goodbye.")
    
    # If no query type has been set, detect query type
    if not session_state["query_type"]:
        response = detect_query_type(user_input)
        return jsonify(response)
    
    # Process the query based on the detected type
    if session_state["query_type"] == "city":
        response = get_fis_in_city(user_input, data)
    elif session_state["query_type"] == "province":
        response = get_cities_in_province(user_input, data)
    elif session_state["query_type"] == "statistics":
        response = "Statistics feature is under development."  # Placeholder for future implementation
    else:
        response = "I don't understand your query. Please ask about cities, provinces, or statistics."

    # After answering the question, ask if the user wants to continue or switch
    follow_up = follow_up_question()
    return jsonify([response, follow_up])

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)
