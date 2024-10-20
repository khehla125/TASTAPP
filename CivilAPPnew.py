import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import folium
from streamlit_folium import st_folium
from dotenv import load_dotenv
import os
import time

# Load environment variables from .env file
load_dotenv()

# Get credentials from environment variables
USERNAME = os.getenv("STREAMLIT_USERNAME")
PASSWORD = os.getenv("STREAMLIT_PASSWORD")

# Function to handle the login process
def login():
    st.title("Login")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    if st.button("Login"):
        if username == USERNAME and password == PASSWORD:
            st.session_state["logged_in"] = True
            st.success("Successfully logged in!")
        else:
            st.error("Invalid username or password")

# Check if the user is logged in
if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False

if not st.session_state["logged_in"]:
    login()
else:
    # Main app content
    BASE_URL = "https://Phillip.pythonanywhere.com/api/datalogger/"

    st.sidebar.header("Select Device")
    device = st.sidebar.selectbox("Choose a device", ["device1", "device2", "device3", "device4", "device5", "device6"])

    def fetch_data(device):
        url = f"{BASE_URL}{device}/"
        response = requests.get(url)
        if response.status_code == 200:
            return response.json()
        else:
            return None

    # Placeholder for dynamic data
    data_placeholder = st.empty()

    # Fetch data for the selected device
    data = fetch_data(device)

    if data:
        # If data is returned, process and display it
        df = pd.DataFrame(data)

        data_placeholder.empty()  # Clear old data

        data_placeholder.header(f"Latest Data for {device}")
        latest_data = df.iloc[-1]
        col1, col2, col3 = data_placeholder.columns(3)
        col1.metric("Temperature (°C)", f"{latest_data['temperature']}")
        col2.metric("Turbidity (NTU)", f"{latest_data['turbidity']}")
        col3.metric("Conductivity (μS/cm)", f"{latest_data['conductivity']}")

        data_placeholder.subheader("Location on Map")
        m = folium.Map(location=[latest_data['latitude'], latest_data['longitude']], zoom_start=12)
        folium.Marker(
            [latest_data['latitude'], latest_data['longitude']],
            popup=f"Device: {device}\nTemperature: {latest_data['temperature']}°C\nTimestamp: {latest_data['timestamp']}",
        ).add_to(m)
        st_folium(m, width=700, height=500)  # Display map using st_folium directly, not through the placeholder

        st.sidebar.subheader("Device Data Table")
        st.sidebar.dataframe(df)

        data_placeholder.subheader("Device Readings Over Time")
        fig = px.line(df, x='timestamp', y=['temperature', 'turbidity', 'conductivity'],
                      labels={'timestamp': 'Timestamp', 'value': 'Reading'},
                      title=f"Readings for {device} Over Time")
        data_placeholder.plotly_chart(fig)

    else:
        # If no data is available, show "Device not activated yet"
        data_placeholder.empty()  # Clear old data
        data_placeholder.header(f"{device} is not activated yet.")

    # Add a small sleep to delay the refresh and prevent looping issues
    time.sleep(1)
    st.experimental_rerun()  # Refresh the page
