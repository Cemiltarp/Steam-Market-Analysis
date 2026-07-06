import pandas as pd
import os
import requests
import time

print("API DATA IS BEING COLLECTED...")

main_folder = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
main_database_filepath = os.path.join(main_folder, "data", "main_database_table.csv")

try:
    df = pd.read_csv(main_database_filepath)
except FileNotFoundError:
    print("ERROR: File not found.")
    exit()

if 'is_free_game' not in df.columns:
    df['is_free_game'] = False       
if 'dlc_number' not in df.columns:
    df['dlc_number'] = 0             
if 'has_mtx' not in df.columns:
    df['has_mtx'] = False            
if 'is_multiplayer' not in df.columns:
    df['is_multiplayer'] = False     
if 'steam_price_without_discount' not in df.columns:
    df['steam_price_without_discount'] = 0.0 
    
if 'release_date' not in df.columns:
    df['release_date'] = "Unknown"

total_games = len(df)

for index, row in df.iterrows():
    appid = row.get('appid')
    if pd.isna(appid): 
        continue
        
    # Steam's regional currency scam has been stopped.
    url = f"https://store.steampowered.com/api/appdetails?appids={int(appid)}&cc=us"
    
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            data = response.json()
            
            if data and str(int(appid)) in data and data[str(int(appid))]['success']:
                details = data[str(int(appid))]['data']
                
                # FREE GAME DETECTION.
                df.at[index, 'is_free_game'] = details.get('is_free', False)
                
                # Number of DLCs.
                dlc_list = details.get('dlc', [])
                df.at[index, 'dlc_number'] = len(dlc_list)
                
                # CATEGORY ANALYSIS (MTX and Multiplayer).
                categories = details.get('categories', [])
                df.at[index, 'has_mtx'] = any(k.get('id') == 35 for k in categories) 
                df.at[index, 'is_multiplayer'] = any(k.get('id') in [1, 9, 36] for k in categories) 
                
                # GLOBAL USD PRICE CORRECTION.
                price_data = details.get('price_overview', {})
                if price_data and not df.at[index, 'is_free_game']:
                    df.at[index, 'steam_price_without_discount'] = float(price_data.get('initial', 0)) / 100.0
                else:
                    df.at[index, 'steam_price_without_discount'] = 0.0

                release_data = details.get('release_date', {})
                df.at[index, 'release_date'] = release_data.get('date', 'Unknown')
                    
            print(f"[{index+1}/{total_games}] {row['name'][:20]:<20} | Release: {df.at[index, 'release_date']} | F2P: {df.at[index, 'is_free_game']} | DLC: {df.at[index, 'dlc_number']} | MTX: {df.at[index, 'has_mtx']} | Price: ${df.at[index, 'steam_price_without_discount']}")                
    except Exception as e:
        print(f"Error ({row['name']}): {str(e)}")
        
    # Safe waiting period for rate limit.
    time.sleep(1.2)

df.to_csv(main_database_filepath, index=False)
print("\nData collection successful.")