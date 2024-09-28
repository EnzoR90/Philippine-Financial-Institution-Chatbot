# Philippine-Financial-Institution-Chatbot
## Abstract
This is a rule-based chatbot that can handle some basic queries about the dataset using natural language processing. 

The dataset named Financial Institution (FI) has been used for my Geographic Information System course at the Carnegie Mellon University. I used two separate datasets namely, (Bangko Sentral ng Pilipinas' Statistics - Physical Network)[https://www.bsp.gov.ph/SitePages/Statistics/BSPhysicalNetwork.aspx] and (Philippines Latitude and Longitude Map)[https://www.mapsofworld.com/lat_long/philippines-lat-long.html]. Before merging the two datasets, I first cleaned the banking statistics to only show the total number of FIs considering the time constraint in finalizing the project. Then I merged both dataset into one using Python programming.

The original project can be accessed using the following ArcGIS Pro links:
**1. Storymap:** (Looking at the Philippines' Financial Inclusion)[https://arcg.is/XTXOa0]

**2. Dashboard:** (Financial Access for Filipinos with a High Poverty Incidence) [https://www.arcgis.com/apps/dashboards/197fe276e52b460dba14668e462f0342 
![image](https://github.com/user-attachments/assets/5920cb53-ec1f-4fde-ae4b-874170145711)]

## Project Information

This is a chatbot built using Flask that provides users with information about the number of financial institutions (FIs) across cities and provinces in the Philippines. The chatbot also provides statistical insights (mean, max, min) for FIs across the country.

## Features

- Ask about the number of financial institutions in specific cities or provinces.
- Query for statistical insights like the mean, max, or min of financial institutions.
- Switch seamlessly between querying cities, provinces, or statistics.

## How to Use

You can start by typing any message like "Hey" to initiate the conversation. The chatbot will guide you through selecting whether you want information about cities, provinces, or statistics.

### Example Queries:

- **City Queries**: 
  - "How many FIs are in Manila?"
  - "What about in Dumaguete?"
  
- **Province Queries**: 
  - "Tell me about financial institutions in Negros Oriental."
  
- **Statistics**: 
  - "Give me statistics for FIs."
  - "What is the average number of FIs?"

To exit the chatbot, type `exit`.

## Installation

To run this chatbot locally:

1. Clone the repository:
   ```bash
   git clone https://github.com/EnzoR90/Philippine-Financial-Institution-Chatbot.git
   cd Philippine-Financial-Institution-Chatbot

2. Install the dependencies:
   ```bash
   pip install -r requirements.txt
     
3. Run the Flask app:
   ```bash
   python FIchatbot.py
   
4. Open index.html in your browser to interact with the chatbot.

## Deployment

The backend is deployed using Railway and the frontend is hosted on GitHub Pages.

	•	Backend (Flask): Deployed on Railway.
	•	Frontend (HTML): Hosted via GitHub Pages.

## Technologies Used

	•	Backend: Python, Flask, pandas, fuzzywuzzy
	•	Frontend: HTML, CSS, JavaScript
	•	Deployment: Railway, GitHub Pages

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Author

Enzo Rodriguez
