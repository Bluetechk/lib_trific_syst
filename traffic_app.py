import streamlit as st
import pandas as pd
from datetime import datetime
import os

# --- Registration/Login Utilities ---
def register_user(email, phone, region):
    user_data = pd.DataFrame([{
        "email": email,
        "phone": phone,
        "region": region
    }])
    if os.path.exists("users.csv"):
        user_data.to_csv("users.csv", mode="a", header=False, index=False)
    else:
        user_data.to_csv("users.csv", index=False)

def user_exists(email):
    if not os.path.exists("users.csv"):
        return False
    df = pd.read_csv("users.csv")
    return email in df["email"].values

def get_user(email):
    if not os.path.exists("users.csv"):
        return None
    df = pd.read_csv("users.csv")
    user = df[df["email"] == email]
    if not user.empty:
        return user.iloc[0].to_dict()
    return None

# --- Registration/Login Page ---
def login_register_page():
    st.title("🔐 Liberia Traffic System")
    st.markdown("Register or log in to receive traffic alerts and updates.")

    mode = st.radio("Choose an option:", ["Login", "Register"])
    with st.form("auth_form"):
        email = st.text_input("Email")
        phone = st.text_input("Phone Number") if mode == "Register" else ""
        region = st.selectbox("Region", ["Montserrado", "Margibi", "Bong", "Grand Bassa", "Nimba", "Lofa", "Other"]) if mode == "Register" else ""
        submit = st.form_submit_button(mode)

    if submit:
        if not email or (mode == "Register" and not phone):
            st.error("Please fill in all required fields.")
            st.stop()
        if mode == "Register":
            if user_exists(email):
                st.error("User already exists. Please log in.")
                st.stop()
            register_user(email, phone, region)
            st.success("Registration successful! You are now logged in.")
            st.session_state["logged_in"] = True
            st.session_state["user_email"] = email
            st.session_state["user_phone"] = phone
            st.session_state["user_region"] = region
        else:  # Login
            if not user_exists(email):
                st.error("User not found. Please register first.")
                st.stop()
            user = get_user(email)
            st.success("Welcome back! You are now logged in.")
            st.session_state["logged_in"] = True
            st.session_state["user_email"] = user["email"]
            st.session_state["user_phone"] = user["phone"]
            st.session_state["user_region"] = user["region"]

# --- Main Dashboard ---
def dashboard():
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

    st.sidebar.image("https://upload.wikimedia.org/wikipedia/commons/5/59/Flag_of_Liberia.svg", width=120)
    st.sidebar.title("Liberia Traffic System")
    st.sidebar.markdown("Monitor and predict traffic congestion in major routes of Monrovia.")

    st.title("🚦 Liberia Traffic Dashboard")
    st.markdown("Get real-time predictions and view historical traffic congestion data.")

    # --- Map Section ---
    st.subheader("🗺️ Traffic Locations Map")
    # Example coordinates for demonstration (Red Light, Sinkor, Duala)
    traffic_locations = pd.DataFrame([
        {"route": "Red Light", "lat": 6.3133, "lon": -10.7125, "congestion": "HEAVY"},
        {"route": "Sinkor", "lat": 6.2827, "lon": -10.7769, "congestion": "MODERATE"},
        {"route": "Duala", "lat": 6.3672, "lon": -10.7922, "congestion": "LIGHT"},
    ])
    st.map(traffic_locations.rename(columns={"lat": "latitude", "lon": "longitude"}))

    # Optionally, show a table with congestion status
    st.dataframe(traffic_locations[["route", "congestion"]])

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

    # Example: Send alert button (optional)
    # from twilio.rest import Client
    # def send_alert(route, status):
    #     client = Client("AC6ed1e2878cdd8c2c4817fb026298865b", "c2117018c9778ac0f819e0a04a0bfa7c")
    #     client.messages.create(
    #         body=f"TRAFFIC ALERT: {route} is {status}!",
    #         from_="+14843715055",
    #         to=st.session_state.get("user_phone", ""),
    #     )
    # if st.button("Confirm Congestion"):
    #     send_alert(route, predict_congestion(route, hour))

def load_data():
    return pd.DataFrame([
        {"route": "Red Light", "hour": 8, "congestion": "HEAVY"},
        {"route": "Sinkor", "hour": 18, "congestion": "MODERATE"},
        {"route": "Duala", "hour": 15, "congestion": "LIGHT"},
        {"route": "Red Light", "hour": 17, "congestion": "HEAVY"},
        {"route": "Sinkor", "hour": 9, "congestion": "MODERATE"},
    ])

def predict_congestion(route, hour):
    if route == "Red Light" and 7 <= hour <= 10:
        return "HEAVY"
    elif route == "Duala" and 15 <= hour <= 18:
        return "LIGHT"
    elif route == "Sinkor" and (8 <= hour <= 9 or 17 <= hour <= 18):
        return "MODERATE"
    return "LIGHT"

# --- Main App Logic ---
if "logged_in" not in st.session_state or not st.session_state["logged_in"]:
    login_register_page()
    st.stop()
else:
    dashboard()
