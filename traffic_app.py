import streamlit as st
import pandas as pd
from datetime import datetime

# Custom CSS for advanced styling
st.markdown("""
    <style>
        .main {background-color: #f5f6fa;}
        .stButton>button {background-color: #273c75; color: white;}
        .stCheckbox>label {font-weight: bold;}
        .congestion-heavy {color: #e84118; font-weight: bold;}
        .congestion-moderate {color: #fbc531; font-weight: bold;}
        .congestion-light {color: #44bd32; font-weight: bold;}
        .report-table td, .report-table th {padding: 8px 16px;}
    </style>
""", unsafe_allow_html=True)

# Mock data for Liberia
def load_data():
    return pd.DataFrame([
        {"route": "Red Light", "hour": 8, "congestion": "HEAVY"},
        {"route": "Sinkor", "hour": 18, "congestion": "MODERATE"},
        {"route": "Duala", "hour": 15, "congestion": "LIGHT"},
        {"route": "Red Light", "hour": 17, "congestion": "HEAVY"},
        {"route": "Sinkor", "hour": 9, "congestion": "MODERATE"},
    ])

# Prediction logic
def predict_congestion(route, hour):
    if route == "Red Light" and 7 <= hour <= 10:
        return "HEAVY"
    elif route == "Duala" and 15 <= hour <= 18:
        return "LIGHT"
    elif route == "Sinkor" and (8 <= hour <= 9 or 17 <= hour <= 18):
        return "MODERATE"
    return "LIGHT"

# Sidebar for navigation and info
st.sidebar.image("https://upload.wikimedia.org/wikipedia/commons/5/59/Flag_of_Liberia.svg", width=120)
st.sidebar.title("Liberia Traffic System")
st.sidebar.markdown("Monitor and predict traffic congestion in major routes of Monrovia.")

# Main title and layout
st.title("🚦 Liberia Traffic Dashboard")
st.markdown("Get real-time predictions and view historical traffic congestion data.")

# Layout with columns
col1, col2 = st.columns([2, 1])

with col1:
    route = st.selectbox("Select Route", ["Red Light", "Sinkor", "Duala"])
    hour = st.slider("Select Hour", 0, 23, datetime.now().hour)
    congestion = predict_congestion(route, hour)
    if congestion == "HEAVY":
        status = f'<span class="congestion-heavy">{congestion}</span>'
    elif congestion == "MODERATE":
        status = f'<span class="congestion-moderate">{congestion}</span>'
    else:
        status = f'<span class="congestion-light">{congestion}</span>'
    st.markdown(f"### {route} at {hour}:00 → Status: {status}", unsafe_allow_html=True)

with col2:
    st.info("**Tip:** Use the controls to get a live prediction for your route and time.")

# Show historical data with styling
if st.checkbox("Show Past Reports"):
    df = load_data()
    def color_congestion(val):
        if val == "HEAVY":
            color = "#e84118"
        elif val == "MODERATE":
            color = "#fbc531"
        else:
            color = "#44bd32"
        return f"color: {color}; font-weight: bold;"
    st.markdown("#### Historical Congestion Reports")
    st.dataframe(df.style.applymap(color_congestion, subset=["congestion"]), height=300)