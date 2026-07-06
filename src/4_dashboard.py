import streamlit as st
import pandas as pd
import numpy as np
import os
import plotly.express as px
import re
from datetime import datetime

st.set_page_config(page_title="Steam Market Prediction", page_icon="📈", layout="wide")

st.title("Steam Global Gaming Market Data Analysis")
st.markdown("API anomalies were corrected using statistical median and adapted to market realities with a Dynamic-Logarithmic ARPU Engine.")
st.markdown("The results do not reflect reality. The calculation is based on an estimate.")
st.divider()

main_folder = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
main_database_filepath = os.path.join(main_folder, "data", "main_database_table.csv")

try:
    df = pd.read_csv(main_database_filepath)
    
    # DATA CLEANING AND MEDIAN PRICE CALCULATION
    
    current_prices = df[df['steam_price_without_discount'] > 0]['steam_price_without_discount']
    median_price = current_prices.median() if not current_prices.empty else 29.99
    
    df['realistic_price'] = np.where(
        (df['is_free_game'] == False) & (df['steam_price_without_discount'] == 0.0), 
        median_price, 
        df['steam_price_without_discount']
    )
    
    # API Bug Fix: We're forcing the MTX tag to be enabled in massively popular games.
    df['has_mtx'] = np.where(df['ccu'] > 20000, True, df['has_mtx'])
    df['is_multiplayer'] = np.where(df['ccu'] > 20000, True, df['is_multiplayer'])

    
    # -ALL TIME AUDIENCE AND SALES ACCOUNT-
  
    df['total_review'] = df['positive'] + df['negative']
    df['multiplier'] = np.where(df['is_free_game'] == True, 45, 30)
    df['estimated_audience'] = df['total_review'] * df['multiplier']
    
    STEAM_ASP_RATIO = 0.65
    df['game_sales_revenue'] = np.where(df['is_free_game'] == False, df['estimated_audience'] * (df['realistic_price'] * STEAM_ASP_RATIO), 0)
    
    
    # -LIVE SERVICE ENGINE AND ARPU-
  
    base_mtx = np.where(df['has_mtx'] & df['is_multiplayer'], 15.0, np.where(df['has_mtx'], 3.0, 0.0))
    dlc_contribution = np.log1p(df['dlc_number']) * 8.0 
    
    # STANDARD ARPU (For all time calculations)
    df['base_in_game_arpu'] = base_mtx + dlc_contribution
    
    # WHALE MULTIPLIER: For the currently active audience only!
    whale_multiplier = np.where(df['ccu'] > 300000, 2.5, np.where(df['ccu'] > 100000, 1.5, 1.0))
    df['live_in_game_arpu'] = df['base_in_game_arpu'] * whale_multiplier
    
    # DYNAMIC PLAYER MULTIPLIER: Current active audience count via CCU
    df['ccu_multiplier'] = np.where(df['ccu'] > 100000, 30.0, np.where(df['ccu'] > 10000, 20.0, 15.0))
    df['active_players'] = df['ccu'] * df['ccu_multiplier']

    
    # -FINANCIAL TURNOVER CALCULATIONS-
   
    # ALL TIME IN-GAME REVENUE
    df['in_game_turnover'] = df['estimated_audience'] * df['base_in_game_arpu']
    
    # ALL-TIME TOTAL REVENUE = Box Sales + All-Time In-Game Revenue
    df['total_revenue'] = df['game_sales_revenue'] + df['in_game_turnover']

    # CURRENT ANNUAL REVENUE = Audience Playing Today Only * ARPU
    df['current_annual_revenue'] = df['active_players'] * df['live_in_game_arpu']
    
    # ALL TIME TOTAL TURNOVER = Box Sales + All Time In-Game Turnover
    df['total_revenue'] = df['game_sales_revenue'] + df['in_game_turnover']

   
    # -GAME AGE AND TABLE HELPERS-
  
    current_year = datetime.now().year
    
    if 'release_date' not in df.columns:
        df['release_date'] = str(current_year) 
        
    def extract_year(date_str):
        match = re.search(r'\d{4}', str(date_str))
        return int(match.group()) if match else current_year

    df['release_year'] = df['release_date'].apply(extract_year)
    df['game_age'] = current_year - df['release_year']
    df['game_age'] = np.where(df['game_age'] < 1, 1, df['game_age'])

   
    # -INTERFACE (UI) AND METRICS-
  
    grand_total_revenue = df['total_revenue'].sum()
    in_game_volume_only = df['in_game_turnover'].sum()
    total_players = df['estimated_audience'].sum()
    
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Market Volume", f"${grand_total_revenue / 1_000_000_000:.2f} Billion")
    col2.metric("In-Game Live Economy", f"${in_game_volume_only / 1_000_000_000:.2f} Billion")
    col3.metric("Total number of accessibility points", f"{total_players / 1_000_000_000:.1f} Billion")
    col4.metric("Filtered Games Count", f"{len(df)} Units")
    
    st.divider()

    st.subheader("Global Market Shares")
    col_pie1, col_pie2 = st.columns(2)
    
    with col_pie1:
        if 'country' in df.columns:
            country_revenue = df.groupby('country')['total_revenue'].sum().sort_values(ascending=False)
            top_countries = country_revenue.head(10)
            other_countries = pd.Series({'Other Markets': country_revenue.iloc[10:].sum()})
            pie_country_df = pd.concat([top_countries, other_countries]).reset_index()
            pie_country_df.columns = ['Country', 'Revenue']
            
            fig_country = px.pie(pie_country_df, values='Revenue', names='Country', 
                              title="Revenue Distribution by Studio Country", 
                              hole=0.4)
            fig_country.update_traces(textposition='inside', textinfo='percent+label')
            st.plotly_chart(fig_country, use_container_width=True)
        else:
            st.warning("Country data not found for pie chart.")
        
    with col_pie2:
        company_revenue = df.groupby('developer')['total_revenue'].sum().sort_values(ascending=False)
        top_companies = company_revenue.head(15).reset_index()
        top_companies.columns = ['Company', 'Revenue']
        
        fig_company = px.pie(top_companies, values='Revenue', names='Company', 
                            title="Power Distribution Among Industry Giants (Top 15)", 
                            hole=0.4)
        fig_company.update_traces(textposition='inside', textinfo='percent')
        st.plotly_chart(fig_company, use_container_width=True)

    st.divider()
    
    st.subheader("📊 Financial Distribution of Games")
    
    
   
  
    games_df = df.sort_values(by='total_revenue', ascending=False).head(5000)
    
  
    display_df = games_df[['name', 'developer', 'release_year', 'game_age', 'ccu', 'current_annual_revenue', 'total_revenue']].copy()

   
    display_df = display_df.rename(columns={
        'name': 'Game Name(or its old name)',
        'developer': 'Developer',
        'release_year': 'Release Year',
        'game_age': 'Game Age',
        'ccu': 'Live Players (CCU)',
        'current_annual_revenue': 'Current Annual Revenue',
        'total_revenue': 'Total Revenue'
    })

   
    display_df['Release Year'] = display_df['Release Year'].apply(lambda x: f"{x}")
    display_df['Game Age'] = display_df['Game Age'].apply(lambda x: f"{x} Years")
    display_df['Live Players (CCU)'] = display_df['Live Players (CCU)'].apply(lambda x: f"{x:,.0f}")
    display_df['Current Annual Revenue'] = display_df['Current Annual Revenue'].apply(lambda x: f"${x:,.0f}")
    display_df['Total Revenue'] = display_df['Total Revenue'].apply(lambda x: f"${x:,.0f}")

    # Printing the table to the screen
    st.dataframe(
        display_df.style.set_properties(
            subset=['Release Year', 'Game Age', 'Live Players (CCU)', 'Current Annual Revenue', 'Total Revenue'], 
            **{'text-align': 'right'}
        ), 
        use_container_width=True, 
        height=800
    )

except FileNotFoundError:
    st.error("Data file not found! Please run data collection scripts first.")