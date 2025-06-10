from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
import pandas as pd

app = Flask(__name__)
reports = []

@app.route("/sms", methods=["POST"])
def sms_reply():
    sender = request.form.get("From")
    message = request.form.get("Body").upper()  # e.g., "REDLIGHT HEAVY"
    
    # Log report
    reports.append({
        "route": message.split()[0],
        "status": message.split()[1],
        "timestamp": pd.Timestamp.now(),
    })
    
    # Reply
    resp = MessagingResponse()
    resp.message(f"Thanks! {len(reports)} drivers reported today.")
    return str(resp)

if __name__ == "__main__":
    app.run(port=5000)