# Philippine-Financial-Institution-Chatbot
## Abstract
This is a rule-based chatbot that can handle some basic queries about the dataset using natural language processing. 

The dataset named Financial Institution (FI) has been used for my Geographic Information System course at the Carnegie Mellon University. I used two separate datasets namely, (Bangko Sentral ng Pilipinas' Statistics - Physical Network)[https://www.bsp.gov.ph/SitePages/Statistics/BSPhysicalNetwork.aspx] and (Philippines Latitude and Longitude Map)[https://www.mapsofworld.com/lat_long/philippines-lat-long.html]. Before merging the two datasets, I first cleaned the banking statistics to only show the total number of FIs considering the time constraint in finalizing the project. Then I merged both dataset into one using Python programming.

The original project can be accessed using the following ArcGIS Pro links:
**1. Storymap:** (Looking at the Philippines' Financial Inclusion)[https://arcg.is/XTXOa0]

**2. Dashboard:** (Financial Access for Filipinos with a High Poverty Incidence) [https://www.arcgis.com/apps/dashboards/197fe276e52b460dba14668e462f0342 
![image](https://github.com/user-attachments/assets/5920cb53-ec1f-4fde-ae4b-874170145711)]

## Project Information

This chatbot allows users to ask about the number of financial institutions (FIs) in cities and provinces across the Philippines, as well as general statistics such as mean, maximum, and minimum FIs.

### Features
- Query FIs in specific cities or provinces
- Get total FIs in a province and a list of cities within it
- Identify the city with the highest and lowest FIs in a province
- General statistics like the average number of FIs across cities

### Installation
1. Clone this repository:
    ```bash
    git clone https://github.com/your-username/financial-inclusion-chatbot.git
    cd financial-inclusion-chatbot
    ```

2. Install the dependencies:
    ```bash
    pip install -r requirements.txt
    ```

3. Run the chatbot:
    ```bash
    python chatbot.py
    ```

### License
This project is licensed under the MIT License.

