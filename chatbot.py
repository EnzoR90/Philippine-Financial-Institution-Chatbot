import pandas as pd
from fuzzywuzzy import fuzz
from fuzzywuzzy import process

# Load the dataset
file_path = 'Updated_FinancialInclusion_Final.csv'
data = pd.read_csv(file_path)

# Prepare city and province lists for matching
cities_list = data['Cities'].str.lower().unique()
provinces_list = data['Province'].str.lower().unique()

# Function to handle fuzzy matching for cities
def get_fis_in_city(city_name, df):
    city_name = city_name.strip().lower()
    df['Cities'] = df['Cities'].str.strip().str.lower()

    # Fuzzy match the city with a threshold of 90 to increase accuracy
    result = process.extractOne(city_name, df['Cities'], scorer=fuzz.partial_ratio)
    
    if result:  # Check if a result is returned
        closest_match, score = result[0], result[1]  # Unpack the closest match and score
        
        if score >= 90:  # Stricter matching threshold
            city_data = df[df['Cities'] == closest_match]
            return city_data[['Cities', 'Province', 'Total Number of Fis']].to_dict(orient='records')
    
    return f"No data found for city: {city_name}"

# Updated Function to handle fuzzy matching for provinces and provide detailed stats
def get_cities_in_province(province_name, df):
    province_name = province_name.strip().lower()
    df['Province'] = df['Province'].str.strip().str.lower()

    # Fuzzy match the province with a stricter threshold of 90
    result = process.extractOne(province_name, df['Province'], scorer=fuzz.partial_ratio)
    
    if result:  # Check if a result is returned
        closest_match, score = result[0], result[1]  # Unpack the closest match and score
        
        if score >= 90:  # Stricter matching threshold for provinces
            # Filter the data for the matched province
            province_data = df[df['Province'] == closest_match]
            
            # List all cities with their FIs
            cities_info = province_data[['Cities', 'Total Number of Fis']].to_dict(orient='records')

            # Calculate the total FIs in the province
            total_fis_in_province = province_data['Total Number of Fis'].sum()

            # Find the city with the highest FIs
            city_with_highest_fis = province_data.loc[province_data['Total Number of Fis'].idxmax()]

            # Find the city with the lowest FIs
            city_with_lowest_fis = province_data.loc[province_data['Total Number of Fis'].idxmin()]

            # Prepare the response with all the details
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

# Function to find the city with the highest/lowest number of financial institutions
def get_city_with_extreme_fis(df, highest=True):
    if highest:
        city_data = df[df['Total Number of Fis'] == df['Total Number of Fis'].max()]
        return city_data[['Cities', 'Province', 'Total Number of Fis']].to_dict(orient='records')
    else:
        city_data = df[df['Total Number of Fis'] == df['Total Number of Fis'].min()]
        return city_data[['Cities', 'Province', 'Total Number of Fis']].to_dict(orient='records')

# Function to get general statistics (average FIs per city)
def get_average_fis(df):
    avg_fis = df['Total Number of Fis'].mean()
    return f"The average number of financial institutions per city is {avg_fis:.2f}"

# Function to detect city or province in the user input using fuzzy matching
def detect_city_or_province(user_input, cities_list, provinces_list):
    user_input = user_input.lower()

    # Fuzzy match city with a higher threshold of 90 for more precise matches
    closest_city = process.extractOne(user_input, cities_list, scorer=fuzz.partial_ratio)
    if closest_city and closest_city[1] >= 90:
        return 'city', closest_city[0]

    # Fuzzy match province with a threshold of 90 for more accurate matches
    closest_province = process.extractOne(user_input, provinces_list, scorer=fuzz.partial_ratio)
    if closest_province and closest_province[1] >= 90:
        return 'province', closest_province[0]

    return None, None

# Main chatbot loop
def chatbot():
    print("Welcome to the Philippine Financial Institutions (FIs) Chatbot! You can ask me about the number of FIs in cities, provinces, or general statistics (e.g., mean, max, min).")
    print("Type 'exit' to end the conversation.")

    while True:
        user_input = input("\nYou: ").lower()

        # Exit condition
        if user_input == "exit":
            print("Goodbye!")
            break

        # Detect if input contains a city or province using fuzzy matching
        entity_type, entity_value = detect_city_or_province(user_input, cities_list, provinces_list)

        # If a city is detected in the input
        if entity_type == 'city':
            response = get_fis_in_city(entity_value, data)
            print(f"\nChatbot: {response}")

        # If a province is detected in the input
        elif entity_type == 'province':
            response = get_cities_in_province(entity_value, data)
            print(f"\nChatbot: {response}")

        # Check for highest financial institutions query (specific keywords)
        elif "highest" in user_input or "most" in user_input:
            response = get_city_with_extreme_fis(data, highest=True)
            print(f"\nChatbot: {response}")

        # Check for lowest financial institutions query
        elif "lowest" in user_input or "fewest" in user_input:
            response = get_city_with_extreme_fis(data, highest=False)
            print(f"\nChatbot: {response}")

        # Check for general statistics query
        elif "average" in user_input or "statistics" in user_input:
            response = get_average_fis(data)
            print(f"\nChatbot: {response}")

        # If no known pattern is matched
        else:
            print("Chatbot: I'm sorry, I don't understand your query. Please ask about cities, provinces, or statistics.")

# Run the chatbot
if __name__ == "__main__":
    chatbot()