import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import folium
from streamlit_folium import st_folium
from dotenv import load_dotenv
import os
import pytz
from datetime import datetime

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

    # Fetch data for the selected device
    data = fetch_data(device)

    if data:
        # If data is returned, process and display it
        df = pd.DataFrame(data)

        # Convert timestamps to SA timezone
        uk_tz = pytz.timezone("Europe/London")
        sa_tz = pytz.timezone("Africa/Johannesburg")

        def convert_to_sa_time(timestamp):
            uk_time = datetime.strptime(timestamp, "%Y-%m-%dT%H:%M:%S%z")  # Adjust format if needed
            sa_time = uk_time.astimezone(sa_tz)
            return sa_time.strftime("%Y-%m-%d %H:%M:%S")

        df["timestamp"] = df["timestamp"].apply(convert_to_sa_time)

        st.header(f"Latest Data for {device}")
        latest_data = df.iloc[-1]
        col1, col2, col3 = st.columns(3)
        col1.metric("Temperature (°C)", f"{latest_data['temperature']}")
        col2.metric("Turbidity (NTU)", f"{latest_data['turbidity']}")
        col3.metric("Conductivity (μS/cm)", f"{latest_data['conductivity']}")

        st.subheader("Location on Map")
        m = folium.Map(location=[latest_data['latitude'], latest_data['longitude']], zoom_start=12)
        folium.Marker(
            [latest_data['latitude'], latest_data['longitude']],
            popup=f"Device: {device}\nTemperature: {latest_data['temperature']}°C\nTimestamp: {latest_data['timestamp']}",
        ).add_to(m)
        st_folium(m, width=700, height=500)

        st.sidebar.subheader("Device Data Table")
        st.sidebar.dataframe(df)

        st.subheader("Device Readings Over Time")
        fig = px.line(df, x='timestamp', y=['temperature', 'turbidity', 'conductivity'],
                      labels={'timestamp': 'Timestamp', 'value': 'Reading'},
                      title=f"Readings for {device} Over Time")
        st.plotly_chart(fig)

    else:
        st.header(f"{device} is not activated yet.")
