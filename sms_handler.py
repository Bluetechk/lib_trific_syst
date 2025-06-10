# sms/sms_handler.py
from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
from dotenv import load_dotenv
import os
import pandas as pd

# Load Twilio credentials
load_dotenv()
account_sid = os.getenv('AC6ed1e2878cdd8c2c4817fb026298865b')
auth_token = os.getenv('c2117018c9778ac0f819e0a04a0bfa7c')
twilio_number = os.getenv('+14843715055')

app = Flask(__name__)

@app.route("/sms", methods=["POST"])
def handle_sms():
    # Extract incoming SMS
    sender = request.form.get("From", "+14843715055")  # e.g., "+231770123456"
    body = request.form.get("Body", "Red light heavy rain").strip().upper()  # e.g., "REDLIGHT HEAVY"
    
    # Log the report (Liberia-specific)
    log_report(sender, body)
    
    # Respond
    resp = MessagingResponse()
    resp.message("🇱🇷 Thanks! Liberia Traffic System received your report.")
    return str(resp)

def log_report(sender, message):
    """Save reports to CSV for analysis"""
    df = pd.DataFrame([{
        "timestamp": pd.Timestamp.now(),
        "number": sender,
        "message": message,
        "route": message.split()[0] if message else "UNKNOWN"
    }])
    
    # Append to existing data or create new file
    if os.path.exists("data/reports.csv"):
        df.to_csv("data/reports.csv", mode="a", header=False, index=False)
    else:
        df.to_csv("data/reports.csv", index=False)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)