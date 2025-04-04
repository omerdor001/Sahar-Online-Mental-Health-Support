import unittest
import subprocess
import requests
import time


class FlaskAppTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Start the Flask app in a background process
        cls.process = subprocess.Popen(
            [
                "python",
                "api/server_api.py",
            ]
        )
        print("Waiting 30 seconds for the app to start...")
        time.sleep(60)  # Wait 60 seconds for the app to fully start

    @classmethod
    def tearDownClass(cls):
        # Terminate the Flask app when done
        cls.process.terminate()
        cls.process.wait()

    def test_login(self):
        """Test the login endpoint."""
        response = requests.post(
            "http://localhost:5000/login",
            json={
                "username": "amitgan",
                "password": "8765432",
                "account_id": "40920689",
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn("token", response.json())

    def test_subscribe(self):
        """Test the subscribe endpoint with a valid token."""
        # First, log in to get a token
        login_response = requests.post(
            "http://localhost:5000/login",
            json={
                "username": "amitgan",
                "password": "87654321",
                "account_id": "40920689",
            },
        )
        token = login_response.json()["token"]
        # Then, try subscribing
        response = requests.post(
            "http://localhost:5000/subscribe",
            headers={"Authorization": token},
            json={"username": "amitgan", "endpoint": "http://dummyendpoint.com/notify"},
        )
        self.assertEqual(response.status_code, 200)

    def test_open_calls(self):
        """Test the open calls endpoint."""
        # Logging in to get a token
        login_response = requests.post(
            "http://localhost:5000/login",
            json={
                "username": "amitgan",
                "password": "87654321",
                "account_id": "40920689",
            },
        )
        token = login_response.json()["token"]
        # Fetch open calls
        response = requests.get(
            "http://localhost:5000/get_open_calls", headers={"Authorization": token}
        )
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.json()["data"], list)

    def test_logout(self):
        """Test logging out."""
        # Log in first to get a token
        login_response = requests.post(
            "http://localhost:5000/login",
            json={
                "username": "amitgan",
                "password": "87654321",
                "account_id": "40920689",
            },
        )
        token = login_response.json()["token"]
        # Log out
        response = requests.post(
            "http://localhost:5000/logout",
            headers={"Authorization": token},
            json={"username": "amitgan"},
        )
        self.assertEqual(response.status_code, 200)


if __name__ == "__main__":
    unittest.main()
