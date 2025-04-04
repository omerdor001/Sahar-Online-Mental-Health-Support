import requests
import threading
from flask import Flask, request, jsonify
import time

# Configuration
BASE_URL = "http://127.0.0.1:5000"
USERNAME = "amitgan"
PASSWORD = "87654321"
ACCOUNT_ID = "40920689"
SUBSCRIBER_PORT = 5002
SUBSCRIBER_ENDPOINT = f"http://127.0.0.1:{SUBSCRIBER_PORT}/notify"

# Setup a Flask app to act as the subscriber
app = Flask(__name__)


@app.route("/notify", methods=["POST"])
def notify():
    data = request.json
    print("Received notification:", data)
    return jsonify({"status": "success", "message": "Data received"})


def run_subscriber_server():
    app.run(port=SUBSCRIBER_PORT, debug=False, use_reloader=False)


# Function to start the subscriber server in a separate thread
def start_subscriber_server():
    threading.Thread(target=run_subscriber_server, daemon=True).start()


def get_jwt():
    response = requests.post(
        f"{BASE_URL}/login",
        json={"username": USERNAME, "password": PASSWORD, "account_id": ACCOUNT_ID},
    )
    return response.json().get("token")


def subscribe(token):
    response = requests.post(
        f"{BASE_URL}/subscribe",
        json={"username": USERNAME, "endpoint": SUBSCRIBER_ENDPOINT},
        headers={"Authorization": token},
    )
    print("Subscribe:", response.text)


def main():
    start_subscriber_server()  # Start the subscriber server
    time.sleep(2)  # Give the server a moment to start
    token = get_jwt()
    if token:
        subscribe(token)
        # Optionally wait and then trigger other API calls
        time.sleep(300)  # Wait to receive notifications


if __name__ == "__main__":
    main()
