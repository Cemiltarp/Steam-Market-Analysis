import pandas as pd
import os
import requests
import time
import pycountry 
import sys
import random
import json
from dotenv import load_dotenv

try:
    from ddgs import DDGS
except ImportError:
    from duckduckgo_search import DDGS

print("COUNTRY SCREENING HAS STARTED...")

load_dotenv()
CLIENT_ID = os.getenv("TWITCH_CLIENT_ID")
CLIENT_SECRET = os.getenv("TWITCH_CLIENT_SECRET")

main_folder = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
search_file_path = os.path.join(main_folder, "data", "search_results_table.csv")
main_database_filepath = os.path.join(main_folder, "data", "main_database_table.csv")

search_df = pd.read_csv(search_file_path)
search_df['total_review'] = search_df['positive'] + search_df['negative']
big_games = search_df[search_df['total_review'] >= 500].copy()

# Main developers' glossary.
local_dictionary = {
    "Valve": "USA", "Rockstar North": "UK", "PUBG Corporation": "South Korea",
    "CAPCOM Co., Ltd.": "Japan", "FromSoftware Inc.": "Japan", 
    "Facepunch Studios": "UK", "Re-Logic": "USA", "Game Science": "China",
    "Grinding Gear Games": "New Zealand", "Bungie": "USA", "Pocketpair": "Japan",
    "Arrowhead Game Studios": "Sweden", "Larian Studios": "Belgium", "Smilegate RPG": "South Korea",
    "TaleWorlds Entertainment": "Turkey", "Klei Entertainment": "Canada", "SCS Software": "Czech Republic"
}

# A dictionary of some searched countries.
wiki_countries = {
    "United States": "USA", "USA": "USA", "California": "USA", "Washington": "USA",
    "United Kingdom": "UK", "UK": "UK", "London": "UK",
    "Germany": "Germany", "German": "Germany", 
    "Sweden": "Sweden", "Swedish": "Sweden",
    "France": "France", "French": "France",
    "Canada": "Canada", "Canadian": "Canada",
    "Japan": "Japan", "Japanese": "Japan",
    "South Korea": "South Korea", "Korean": "South Korea",
    "China": "China", "Chinese": "China",
    "Russia": "Russia", "Russian": "Russia",
    "Poland": "Poland", "Polish": "Poland",
    "Cyprus": "Cyprus", "Cyprus Republic": "Cyprus",
    "Singapore": "Singapore"
}

def twitch_token_request():
    url = "https://id.twitch.tv/oauth2/token"
    response = requests.post(url, params={"client_id": CLIENT_ID, "client_secret": CLIENT_SECRET, "grant_type": "client_credentials"})
    return response.json().get("access_token")

headers = {"Client-ID": CLIENT_ID, "Authorization": f"Bearer {twitch_token_request()}"}

new_country_dictionary = {}
best_developers = big_games['developer'].unique()

# Temporary index pool.
temporary_data_file = 'recovery_data.json'
rescue_pool = {}

if os.path.exists(temporary_data_file):
    # 12-Hour Time Control.
    file_age = time.time() - os.path.getmtime(temporary_data_file)
    if file_age > 12 * 3600:
        print("Recovery pool was reset because it was older than 12 hours.")
        try:
            os.remove(temporary_data_file)
        except Exception:
            pass
    else:
        with open(temporary_data_file, 'r', encoding='utf-8') as f:
            rescue_pool = json.load(f)

for studio in best_developers:
    # Skip if cell is empty
    if pd.isna(studio) or not isinstance(studio, str):
        continue
    
    # Check the fixed dictionary.
    if studio in local_dictionary:
        new_country_dictionary[studio] = local_dictionary[studio]
        print(f"[DICTIONARY] {studio} -> {local_dictionary[studio]}")
        continue 
        
    # Temporary search data recovery
    if studio in rescue_pool:
        new_country_dictionary[studio] = rescue_pool[studio]
        print(f"[TEMPORARY DATA] {studio} -> {rescue_pool[studio]}")
        continue
        
    first_word = studio.split(',')[0].split('&')[0].strip().split()[0].replace("'", "").replace('"', '')
    
    # TWITCH (IGDB)
    query = f'fields name, country; where name ~ *"{first_word}"* | name ~ *"{first_word.capitalize()}"*; limit 5;'
    reply = requests.post("https://api.igdb.com/v4/companies", headers=headers, data=query)
    
    country_name = "Unknown"
    was_it_found = False
    
    if reply.status_code == 200:
        data = reply.json()
        for s in data:
            if 'country' in s:
                country_code = str(s['country']).zfill(3) 
                country_object = pycountry.countries.get(numeric=country_code)
                
                if country_object:
                    English_name = country_object.name
                    country_name = wiki_countries.get(English_name, English_name)
                else:
                    country_name = f"Unknown Code ({country_code})"
                    
                was_it_found = True
                print(f"[TWITCH FOUND IT] {studio} -> {country_name}")
                break
    
    # WIKIPEDIA
    if not was_it_found:
        search_term = studio.split(',')[0].replace("Team", "").replace("Studios", "").replace("Inc.", "").strip()
        wiki_url = f"https://en.wikipedia.org/w/api.php?action=query&list=search&srsearch={search_term}&utf8=&format=json"
        wiki_answer = requests.get(wiki_url)
        
        if wiki_answer.status_code == 200 and len(wiki_answer.json().get('query', {}).get('search', [])) > 0:
            wiki_text = wiki_answer.json()['query']['search'][0]['snippet']
            for English_word, country_val in wiki_countries.items():
                if English_word.lower() in wiki_text.lower():
                    country_name = country_val
                    was_it_found = True
                    print(f"[FOUND BY WIKIPEDIA] {studio} -> {country_name}")
                    break

    # DUCKDUCKGO
    if not was_it_found:
        ddg_query = f"{search_term} developer headquarters country location"
        successful_query = False
        
        while not successful_query:
            try:
                time.sleep(random.uniform(1.5, 3.5))
                
                with DDGS() as ddgs:
                    ddg_results = list(ddgs.text(ddg_query, max_results=3))
                    for result in ddg_results:
                        snippet = result.get('body', '') + " " + result.get('title', '')
                        for English_word, country_val in wiki_countries.items():
                            if English_word.lower() in snippet.lower():
                                country_name = country_val
                                was_it_found = True
                                print(f"[FOUND BY WEB SEARCH] {studio} -> {country_name}")
                                break
                        if was_it_found:
                            break
                            
                successful_query = True 
                
            except Exception as e:
                print(f"\n[WEB RESTRICTION] DuckDuckGo rate limit hit!")
                waiting_time = 20 * 60 
                
                for remaining in range(waiting_time, 0, -1):
                    minute, second = divmod(remaining, 60)
                    sys.stdout.write(f"\rTime remaining until ban lifted: {minute:02d}:{second:02d} ")
                    sys.stdout.flush()
                    time.sleep(1)
                    
                print("\nSearch triggered again.\n")

    if not was_it_found:
        country_name = "Independent / Unknown"
        print(f"Independent / Unknown {studio}")

    # Update rescue pool
    new_country_dictionary[studio] = country_name
    rescue_pool[studio] = country_name 

    with open(temporary_data_file, 'w', encoding='utf-8') as f:
        json.dump(rescue_pool, f, ensure_ascii=False, indent=4)

    time.sleep(0.3) 

# We are updating the main data repository.
big_games['country'] = big_games['developer'].map(new_country_dictionary)
big_games.to_csv(main_database_filepath, index=False)
print("\nThe table is ready for the Dashboard.")