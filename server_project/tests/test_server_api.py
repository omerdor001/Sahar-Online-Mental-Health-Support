import pytest
import requests
from unittest.mock import patch
from faker import Faker

# Add this to handle the import path issue
import sys
import os

# Adjust the sys.path to ensure the correct module can be found
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from api.server_api import ServerAPI  # Importing the ServerAPI from the correct path

fake = Faker()

@patch('api.server_api.requests.get')
def test_successful_api_call(mock_get):
    api_url = fake.url()
    expected_response = {fake.word(): fake.word()}
    mock_get.return_value.status_code = 200
    mock_get.return_value.json.return_value = expected_response

    server_api = ServerAPI(api_url)
    response = server_api.get_data()

    assert response == expected_response
    mock_get.assert_called_once_with(api_url)

@patch('api.server_api.requests.get')
def test_api_call_failure(mock_get):
    api_url = fake.url()
    error_message = fake.sentence()
    mock_get.return_value.status_code = 404
    mock_get.return_value.json.return_value = {"error": error_message}

    server_api = ServerAPI(api_url)
    response = server_api.get_data()

    assert response == {"error": error_message}
    mock_get.assert_called_once_with(api_url)

@patch('api.server_api.requests.get')
def test_api_call_timeout(mock_get):
    api_url = fake.url()
    mock_get.side_effect = requests.exceptions.Timeout

    server_api = ServerAPI(api_url)
    response = server_api.get_data()

    assert response is None
    mock_get.assert_called_once_with(api_url)

@patch('api.server_api.requests.get')
def test_invalid_json_response(mock_get):
    api_url = fake.url()
    mock_get.return_value.status_code = 200
    mock_get.return_value.json.side_effect = ValueError("Invalid JSON")

    server_api = ServerAPI(api_url)
    response = server_api.get_data()

    assert response is None
    mock_get.assert_called_once_with(api_url)