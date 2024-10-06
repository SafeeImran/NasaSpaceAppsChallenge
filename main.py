import streamlit as st
import pandas as pd
from ipyvizzu import Data, Chart, Config, DisplayTarget, Style
import numpy as np
from streamlit_folium import folium_static
import folium
from folium.plugins import HeatMap
import matplotlib.pyplot as plt
import random
import os
import re
import time
import google.generativeai as genai

# Configure the API key for Google Generative AI
os.environ['GOOGLE_API_KEY'] = "AIzaSyDE1vp33z8kjpf0AlbPmmzRm9aougE0oLM"

# Function to configure Gemini AI
def configure_gemini():
    genai.configure(api_key=os.environ["GOOGLE_API_KEY"])  # Replace YOUR_API_KEY with your actual API key

# Define the CropX AI Page
def cropx_ai_page():
    st.title("CropX AI")
    st.write("Welcome to the CropX AI page!")
    st.write("Here, we will provide AI-driven insights and predictive analysis on crop health, yield, and other factors.")

    # Example placeholder content for CropX AI
    st.write("Predictive models and insights will be displayed here.")
    
    # Set the title of the app
    st.title("Agriculture Chatbot")

    # Create a text input for user questions
    user_input = st.text_input("Ask a question about agriculture:" + "      Questions unrelated to agriculture will not be answered by the chat bot.")

    # Function to check if the question is related to agriculture
    def is_agriculture_related(question):
        agriculture_keywords = r'\b(agriculture|farming|crops|soil|irrigation|pesticides|fertilizers|livestock|harvest|sustainability|agronomy|horticulture|agricultural technology)\b'
        return bool(re.search(agriculture_keywords, question, re.IGNORECASE))

    # Function to call the Gemini API
    def generate_response(prompt):
        model = genai.GenerativeModel(model_name="gemini-1.5-flash")
        response = model.generate_content(prompt)
        return response.text

    # Check if user input is provided
    if user_input:
        if is_agriculture_related(user_input):
            response = generate_response(user_input)
            st.write("**AI Response:**")
            st.write(response)
        else:
            st.write("**AI Response:** Sorry, I can only answer questions related to agriculture. Please ask something about farming, crops, soil, irrigation, or related topics.")

# Function to generate the heatmap and statistics for weather factors
def generate_all_factors_heatmap(df, city_coords):
    avg_data = df.groupby('City')[['precipitation', 'wind', 'soil moisture', 'humidity']].mean().reset_index()
    m = folium.Map(location=[31.5820, 73.0569], zoom_start=6, tiles="OpenStreetMap")

    # Create HeatMaps
    for factor in ['precipitation', 'wind', 'soil moisture', 'humidity']:
        heat_data = [
            [city_coords[row['City']][0], city_coords[row['City']][1], row[factor]]
            for index, row in avg_data.iterrows()
        ]
        HeatMap(heat_data, name=factor.capitalize(), max_val=max(avg_data[factor]), radius=25).add_to(m)

    folium.LayerControl().add_to(m)
    return m, avg_data

def create_sample_data():
    cities = ['Attock', 'Rawalpindi', 'Jhelum', 'Chakwal', 'Talagang', 'Sargodha', 'Toba Tek Singh', 'Chiniot', 'Mianwali', 'Jhang']
    data = []
    for city in cities:
        for day in range(1, 8):  # 7 days
            day_data = {
                'City': city,
                'Date': f'2024-10-{day:02d}',  # Dates from 2024-10-01 to 2024-10-07
                'precipitation': np.random.randint(0, 100),
                'wind': np.random.randint(0, 20),
                'soil moisture': np.random.randint(10, 50),
                'humidity': np.random.randint(40, 90),
            }
            data.append(day_data)
    df = pd.DataFrame(data)
    return df

# Coordinates for each city
city_coords = {
    'Attock': (33.7731, 72.3604),
    'Rawalpindi': (33.6844, 73.0479),
    'Jhelum': (32.9417, 73.7284),
    'Chakwal': (32.9335, 72.8549),
    'Talagang': (32.9304, 72.4158),
    'Sargodha': (32.0836, 72.6713),
    'Toba Tek Singh': (30.9743, 72.4827),
    'Chiniot': (31.7208, 72.9786),
    'Mianwali': (32.5864, 71.5436),
    'Jhang': (31.3068, 72.3281)
}

# Sidebar for navigation
st.sidebar.image("assets/logo.png", use_column_width=True)  # Add your logo here
st.sidebar.title("Navigation")
st.sidebar.markdown("<h4 style='text-align: center;'>Making Data Visualization Easier for Farmers</h4>", unsafe_allow_html=True)  # Animated Title
st.sidebar.markdown("""
<style>
@keyframes pulse {
  0% { opacity: 0.5; }
  50% { opacity: 1; }
  100% { opacity: 0.5; }
}
h4 {
  animation: pulse 1.5s infinite;
}
</style>
""", unsafe_allow_html=True)

page = st.sidebar.radio("Go to", ["Main Dashboard", "CropX AI"])

# Main Dashboard Functionality
if page == "Main Dashboard":
    st.title("Agricultural Data Dashboard")  # Main Title
    st.subheader("Insights and Predictive Analysis for Farmers")  # Subtitle

    st.sidebar.title("Options")
    province = st.sidebar.selectbox("Pick a province", ("Sindh", "Punjab", "Balochistan", "KPK"))

    if province == "Punjab":
        df = create_sample_data()
        tab1, tab2 = st.tabs(["Overview", "Yield Statistics"])

        with tab1:
            heatmap, avg_data = generate_all_factors_heatmap(df, city_coords)
            col1, col2 = st.columns([2, 1.85])

            with col1:
                st.write("Weather Factors Heatmap")
                folium_static(heatmap, height=1000, width=600)

            with col2:
                st.sidebar.title("Select a City")
                city = st.sidebar.selectbox("Choose a city", df['City'].unique())
                city_data = df[df['City'] == city]
                st.write(f"Weather Data for {city}:")

                styled_df = city_data.style.applymap(lambda val: 'color: red' if val > 60 or val < 10 else 'color: green', subset=['precipitation', 'wind', 'soil moisture', 'humidity'])
                st.dataframe(styled_df.set_table_attributes('style="text-align: right;"'), width=700, height=300)

                city_data_melted = city_data.melt(id_vars=["Date", "City"], value_vars=["precipitation", "wind", "soil moisture", "humidity"], var_name="Weather Factor", value_name="Value")

                data = Data()
                data.add_data_frame(city_data_melted)
                chart = Chart(width="640px", height="360px", display=DisplayTarget.MANUAL)

                chart.animate(data)
                chart.animate(Config({"channels": {"x": "Date", "y": ["Weather Factor", "Value"], "color": "Weather Factor"}, "geometry": "area"}))
                chart.animate(Config({"channels": {"y": "Value"}, "geometry": "circle"}))
                chart.feature("tooltip", True)
                st.components.v1.html(chart._repr_html_(), height=600)

            st.title("Average Weather Factors")

        with tab2:
            def display_yield_statistics():
                cities = ['Attock', 'Rawalpindi', 'Jhelum', 'Chakwal', 'Talagang']
                data = {'City': [], 'Yield Production (%)': [], 'Yield Loss (%)': []}
                
                for city in cities:
                    data['City'].append(city)
                    data['Yield Production (%)'].append(random.randint(50, 100))
                    data['Yield Loss (%)'].append(random.randint(0, 50))

                yield_data = pd.DataFrame(data)

                st.title("Yield Production and Loss Overview")  # General title for all cities

                # Reshape data for plotting
                yield_data_melted = yield_data.melt(id_vars=["City"], value_vars=["Yield Production (%)", "Yield Loss (%)"],
                                                    var_name="Category", value_name="Value")

                # Create a line graph
                chart = Chart(width="1280px", height="720px", display=DisplayTarget.MANUAL)
                data = Data()
                data.add_data_frame(yield_data_melted)

                chart.animate(data)
                chart.animate(Config({
                    "channels": {
                        "x": "City",
                        "y": "Value",
                        "color": "Category"
                    },
                    "geometry": "line"
                }))
                chart.feature("tooltip", True)
                st.components.v1.html(chart._repr_html_(), height=800)

        # Call the updated display_yield_statistics function
            display_yield_statistics()

# CropX AI Page
elif page == "CropX AI":
    cropx_ai_page()

# Add GitHub link at the end of the sidebar
st.sidebar.markdown("---")  # Separator line
st.sidebar.markdown("[GitHub Repository](https://github.com/SafeeImran)")

# Call the function to configure Gemini
configure_gemini()
