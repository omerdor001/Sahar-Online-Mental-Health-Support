import requests
import time

# Configuration
BASE_URL = "http://127.0.0.1:5000"
USERNAME = "BGU_TEST_1"
PASSWORD = "SaharTest123"
ACCOUNT_ID = "40920689"


def get_jwt():
    """Log in to get a JWT."""
    response = requests.post(
        f"{BASE_URL}/login",
        json={"username": USERNAME, "password": PASSWORD, "account_id": ACCOUNT_ID},
    )
    if response.status_code == 200:
        return response.json()["token"]
    else:
        print("Failed to get JWT:", response.text)
        return None


def subscribe(token):
    """Subscribe to updates."""
    response = requests.post(
        f"{BASE_URL}/subscribe",
        json={
            "username": USERNAME,
            "endpoint": "http://dummyurl.com/notify",  # This should be a valid URL your server can reach
        },
        headers={"Authorization": token},
    )
    print("Subscribe:", response.text)


def get_open_calls(token):
    """Get open calls."""
    response = requests.get(
        f"{BASE_URL}/get_open_calls", headers={"Authorization": token}
    )
    print("Open Calls:", response.text)


def get_history_calls(token):
    """Get call history."""
    response = requests.get(
        f"{BASE_URL}/get_history_calls", headers={"Authorization": token}
    )
    print("History Calls:", response.text)


def get_conversation_data_by_id(token, conversation_id):
    """Get conversation data by ID."""
    response = requests.get(
        f"{BASE_URL}/get_conversation_data_by_id",
        headers={"Authorization": token},
        params={"id": conversation_id},
    )
    print("Conversation Data:", response.text)


def logout(token):
    """Log out and unsubscribe."""
    response = requests.post(
        f"{BASE_URL}/logout",
        json={"username": USERNAME},
        headers={"Authorization": token},
    )
    print("Logout:", response.text)


def main():
    token = get_jwt()
    if token:
        subscribe(token)
        time.sleep(2)  # Wait for subscription processing
        get_open_calls(token)
        get_history_calls(token)
        get_conversation_data_by_id(
            token, "2355e0fd-4a60-4c2f-8406-2f35f15caef7"
        )  # Assuming '1' is a valid conversation ID
        logout(token)


if __name__ == "__main__":
    main()
