import streamlit as st
import pandas as pd
from datetime import datetime
import os
import requests
from dotenv import load_dotenv
load_dotenv()

# --- Custom CSS for Classic UI ---
st.markdown("""
    <style>
        body {
            background-color: #f4f6f8;
        }
        .main {
            background-color: #fff;
            border-radius: 12px;
            padding: 2rem 2rem 1rem 2rem;
            box-shadow: 0 2px 8px rgba(44,62,80,0.07);
            margin-bottom: 2rem;
        }
        .stSidebar {
            background: #273c75 !important;
        }
        .stButton>button {
            background-color: #273c75;
            color: white;
            border-radius: 6px;
            font-weight: bold;
        }
        .stRadio>label, .stSelectbox>label, .stTextInput>label {
            font-weight: bold;
        }
        .congestion-heavy {color: #e84118; font-weight: bold;}
        .congestion-moderate {color: #fbc531; font-weight: bold;}
        .congestion-light {color: #44bd32; font-weight: bold;}
        footer {visibility: hidden;}
    </style>
""", unsafe_allow_html=True)

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
    st.markdown('<h1 style="color:#273c75;"><i class="bi bi-shield-lock"></i> Liberia Traffic System</h1>', unsafe_allow_html=True)
    st.markdown("""
        <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.10.5/font/bootstrap-icons.css">
    """, unsafe_allow_html=True)
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
    st.markdown('<div class="main">', unsafe_allow_html=True)
    st.markdown('<h2 style="color:#273c75;">🚦 Liberia Traffic Dashboard</h2>', unsafe_allow_html=True)
    st.markdown("Get real-time predictions and view historical traffic congestion data.")

    # --- Map Section ---
    st.markdown('<h4 style="color:#192a56;"><i class="bi bi-geo-alt-fill"></i> Traffic Locations Map</h4>', unsafe_allow_html=True)
    traffic_locations = pd.DataFrame([
        {"route": "Red Light", "lat": 6.3133, "lon": -10.7125, "congestion": "HEAVY"},
        {"route": "Sinkor", "lat": 6.2827, "lon": -10.7769, "congestion": "MODERATE"},
        {"route": "Duala", "lat": 6.3672, "lon": -10.7922, "congestion": "LIGHT"},
    ])
    st.map(traffic_locations.rename(columns={"lat": "latitude", "lon": "longitude"}))
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
        st.dataframe(df.style.map(color_congestion, subset=["congestion"]), height=400)
    st.markdown('</div>', unsafe_allow_html=True)

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

# --- Chatbot Page ---
def chatbot_page():
    st.markdown('<div class="main">', unsafe_allow_html=True)
    st.title("🤖 Liberia Traffic Chatbot")
    
    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        st.error("API key missing! Add OPENROUTER_API_KEY to .env")
        return

    if "chat_history" not in st.session_state:
        st.session_state.chat_history = [
            {"role": "system", "content": "You're a Liberian traffic assistant. Use short answers with emojis."}
        ]

    for msg in st.session_state.chat_history[1:]:
        st.chat_message(msg["role"]).write(msg["content"])

    if user_input := st.chat_input("Ask about traffic..."):
        st.session_state.chat_history.append({"role": "user", "content": user_input})
        headers = {
            "Authorization": f"Bearer {api_key}",
            "HTTP-Referer": "https://liberia-traffic.streamlit.app",
            "X-Title": "Liberia Traffic Bot",
            "Content-Type": "application/json"
        }
        payload = {
            "model": "deepseek-chat",
            "messages": st.session_state.chat_history,
        }
        try:
            with st.spinner("Checking traffic..."):
                response = requests.post(
                    "https://openrouter.ai/api/v1/chat/completions",
                    headers=headers,
                    json=payload,
                    timeout=30
                )
                response.raise_for_status()
                ai_content = response.json()["choices"][0]["message"]["content"]
        except requests.exceptions.HTTPError as e:
            st.error(f"API Error: {e.response.text}")
            ai_content = "⚠️ Temporary network issue. Try again."
        st.session_state.chat_history.append({"role": "assistant", "content": ai_content})
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

# --- Map Page ---
def view_map_page():
    st.markdown('<div class="main">', unsafe_allow_html=True)
    st.markdown('<h2 style="color:#273c75;">🗺️ Liberia Live Traffic Map</h2>', unsafe_allow_html=True)
    st.markdown("See live traffic with Waze and compare with system data below.")

    # Embed Waze Live Map (centered on Monrovia, Liberia)
    st.markdown(
        """
        <iframe src="https://embed.waze.com/iframe?zoom=13&lat=6.3008&lon=-10.7972"
                width="100%" height="500" allowfullscreen></iframe>
        """,
        unsafe_allow_html=True
    )

    # Optionally, show your own traffic data below
    traffic_locations = pd.DataFrame([
        {"route": "Red Light", "lat": 6.3133, "lon": -10.7125, "congestion": "HEAVY"},
        {"route": "Sinkor", "lat": 6.2827, "lon": -10.7769, "congestion": "MODERATE"},
        {"route": "Duala", "lat": 6.3672, "lon": -10.7922, "congestion": "LIGHT"},
    ])
    st.markdown("#### System Traffic Data")
    st.map(traffic_locations.rename(columns={"lat": "latitude", "lon": "longitude"}))
    st.dataframe(traffic_locations[["route", "congestion"]])
    st.markdown('</div>', unsafe_allow_html=True)

# --- Main App Logic with Sidebar Navigation ---
def main():
    st.sidebar.image("https://flagcdn.com/w320/lr.png", width=120)
    st.sidebar.title("Liberia Traffic System")
    st.sidebar.markdown(
        """
        <style>
            .sidebar-content {background-color: #273c75; color: white;}
        </style>
        """,
        unsafe_allow_html=True
    )
    menu = ["Home", "View Map", "Historical Data", "Chatbot"]
    if "logged_in" not in st.session_state or not st.session_state["logged_in"]:
        menu = ["Login/Register"] + menu
    choice = st.sidebar.radio("Navigation", menu)

    if choice == "Login/Register":
        login_register_page()
    elif "logged_in" not in st.session_state or not st.session_state["logged_in"]:
        st.warning("Please log in or register to access the dashboard.")
        login_register_page()
    elif choice == "Home":
        dashboard()
    elif choice == "View Map":
        view_map_page()
    elif choice == "Historical Data":
        dashboard()  # You can split this if you want a separate historical data page
    elif choice == "Chatbot":
        chatbot_page()

    # Footer
    st.markdown(
        """
        <hr>
        <center style="color:#888;font-size:0.9em;">
            Liberia Traffic System &copy; 2025 | Powered by Streamlit
        </center>
        """,
        unsafe_allow_html=True
    )

if __name__ == "__main__":
    main()