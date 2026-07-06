import requests
import pandas as pd
import time
from datetime import datetime
import os

print("GAME SEARCH HAS STARTED...")

# File paths.
main_folder = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
data_folder = os.path.join(main_folder, "data")
if not os.path.exists(data_folder):
    os.makedirs(data_folder)
search_file_path = os.path.join(data_folder, "search_results_table.csv")

all_games_list = []

# Pages containing 5000 games.
TARGET_PAGE_COUNT = 5 

for page in range(TARGET_PAGE_COUNT):
    print(f"Region {page+1}/{TARGET_PAGE_COUNT} being scanned (Page: {page})...")
    url = f"https://steamspy.com/api.php?request=all&page={page}"
    
    try:
        response = requests.get(url, timeout=15)
        if response.status_code == 200:
            raw_data = response.json()
            
            # We convert the JSON formatted data into a Pandas-compatible list
            page_games = list(raw_data.values())
            all_games_list.extend(page_games)
        else:
            print(f"Page {page} Server error: {response.status_code}")
            
    except Exception as e:
        print(f"Page {page} An error occurred while retrieving: {str(e)}")
        
    # Wait 2 seconds to avoid getting banned.
    time.sleep(2)

# Convert tens of thousands of collected data points into a Pandas table.
table = pd.DataFrame(all_games_list)

filtered_table = table[['appid', 'name', 'developer', 'positive', 'negative', 'price', 'ccu']]

# Clean up duplicate records based on AppID.
filtered_table = filtered_table.drop_duplicates(subset=['appid'])

today_date = datetime.now().strftime("%Y-%m-%d")
filtered_table['search_date'] = today_date

filtered_table.to_csv(search_file_path, index=False)

game_count = len(filtered_table)
print(f"\nSuccessfully saved {game_count} games to the data folder.")