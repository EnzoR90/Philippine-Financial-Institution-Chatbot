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

# Fuzzy matching functions
def get_fis_in_city(city_name, df):
    city_name = city_name.strip().lower()
    df['Cities'] = df['Cities'].str.strip().str.lower()

    result = process.extractOne(city_name, df['Cities'], scorer=fuzz.partial_ratio)
    
    if result:
        closest_match, score = result[0], result[1]
        if score >= 80:  # Adjusted matching threshold
            city_data = df[df['Cities'] == closest_match]
            return city_data[['Cities', 'Province', 'Total Number of Fis']].to_dict(orient='records')
    
    return f"No data found for city: {city_name}"

# New version of get_cities_in_province to list all cities
def get_cities_in_province(province_name, df):
    province_name = province_name.strip().lower()
    df['Province'] = df['Province'].str.strip().str.lower()
    
    result = process.extractOne(province_name, df['Province'], scorer=fuzz.partial_ratio)
    
    if result:
        closest_match, score = result[0], result[1]
        if score >= 90:
            province_data = df[df['Province'] == closest_match]
            cities_info = province_data[['Cities', 'Total Number of Fis']].to_dict(orient='records')
            
            # Total FIs in the province
            total_fis_in_province = province_data['Total Number of Fis'].sum()
            
            # Find the city with the highest and lowest number of FIs
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

# Function to get statistics for the dataset
def get_statistics(df, stat_type):
    if stat_type == "mean" or stat_type == "average":
        avg_fis = df['Total Number of Fis'].mean()
        return f"The average number of financial institutions per city is {avg_fis:.2f}"
    elif stat_type == "max" or stat_type == "highest":
        max_fis_city = df.loc[df['Total Number of Fis'].idxmax()]
        return f"{max_fis_city['Cities']} has the highest number of financial institutions with {max_fis_city['Total Number of Fis']} FIs."
    elif stat_type == "min" or stat_type == "lowest":
        min_fis_city = df.loc[df['Total Number of Fis'].idxmin()]
        return f"{min_fis_city['Cities']} has the lowest number of financial institutions with {min_fis_city['Total Number of Fis']} FIs."
    return "Statistics type not recognized. Please ask for 'mean', 'max', or 'min'."

# Function to detect the type of query (city, province, or statistics)
def detect_query_type(user_input, cities_list, provinces_list):
    user_input = user_input.lower()

    # Handle the 'exit' command
    if "exit" in user_input:
        return 'exit', None

    # Check if the query contains a statistic keyword
    if any(stat in user_input for stat in ["mean", "average", "max", "highest", "min", "lowest"]):
        return 'statistic', user_input
    
    # Fuzzy match for cities
    closest_city = process.extractOne(user_input, cities_list, scorer=fuzz.partial_ratio)
    if closest_city and closest_city[1] >= 80:
        return 'city', closest_city[0]

    # Fuzzy match for provinces
    closest_province = process.extractOne(user_input, provinces_list, scorer=fuzz.partial_ratio)
    if closest_province and closest_province[1] >= 80:
        return 'province', closest_province[0]

    return None, None

# Flask route to interact with the chatbot
@app.route('/chatbot', methods=['GET', 'POST'])
def chatbot():
    if request.method == 'GET':
        return "Chatbot is running. Please use POST requests."
    
    user_input = request.json.get('query', '').lower()
    query_type, query_value = detect_query_type(user_input, cities_list, provinces_list)

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
