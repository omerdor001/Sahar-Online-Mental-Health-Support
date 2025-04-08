import time
from concurrent.futures import ThreadPoolExecutor
from selenium import webdriver
from selenium.webdriver.common.by import By

import json

import requests

# Function to perform the login test for each user
def login_test(user_details):
    # Set up WebDriver (ensure each thread has its own instance)
    driver = webdriver.Chrome()  # Or use any other driver like Firefox, Edge, etc.

    try:
        driver.get("https://saharassociation.cs.bgu.ac.il/test/")  # Replace with the actual URL

        time.sleep(3)

        # Fill in the login form
        account_number = driver.find_element(By.XPATH, "/html/body/div/div/div/div/div/form/div[1]/div/input")
        account_number.send_keys(user_details['account_number'])

        user_name = driver.find_element(By.XPATH, "/html/body/div/div/div/div/div/form/div[2]/div/input")
        user_name.send_keys(user_details['user_name'])

        password = driver.find_element(By.XPATH, "/html/body/div/div/div/div/div/form/div[3]/div/input")
        password.send_keys(user_details['password'])

        radio_but = driver.find_element(By.XPATH, "/html/body/div/div/div/div/div/form/div[4]/label[2]/span[1]/input")
        radio_but.click()

        connect = driver.find_element(By.XPATH, "/html/body/div/div/div/div/div/form/button")
        connect.click()

        time.sleep(5)
        nir = driver.find_element(By.XPATH, "//h4[contains(text(), 'שיחות פעילות')]")

        try:
            close_alarm = driver.find_element(By.XPATH,"/html/body/div[2]/div[3]/button")
            close_alarm.click()
        except Exception as e:
            print(f"exception is {e}" )
        conversation_id = 'f9dd135b-b81d-434a-a07a-a8a270b6969d'

        filter_by_id = driver.find_element(By.XPATH, "/html/body/div/div/div/div/div/div[2]/div/div/input")
        filter_by_id.send_keys(conversation_id)
        time.sleep(2)
        conv = driver.find_element(By.XPATH, "/html/body/div/div/div/div/div/div[3]/div/div[2]/div/div[4]/p")

        burger_icon = driver.find_element(By.XPATH,"/html/body/div[1]/div/div/div/button")
        burger_icon.click()

        settings_icon = driver.find_element(By.XPATH, "/html/body/div[1]/div/div/div/div[1]/button[2]")
        settings_icon.click()

        list_chosen = driver.find_element(By.XPATH, "/html/body/div[1]/div/div/div/div/div[2]/div/div/div")
        list_chosen.click()

        one_minute_option = driver.find_element(By.XPATH,"/html/body/div[2]/div[3]/ul/li[1]")
        one_minute_option.click()


        # it works until here
        burger_icon2 = driver.find_element(By.XPATH,"/html/body/div/div/div/div/button")
        burger_icon2.click()

        home_page = driver.find_element(By.XPATH, "/html/body/div/div/div/div/div[1]/button[1]")
        home_page.click()
        time.sleep(60)  # Allow time for login to process
        try:
            close_alarm = driver.find_element(By.XPATH,"/html/body/div[2]/div[3]/button")
            close_alarm.click()
        except Exception as e:
            print(f"exception is {e}" )
        print(f"User {user_details['user_name']} logged in successfully and conversation_id exist")

    finally:
        driver.quit()  # Ensure the WebDriver instance is closed properly

def login_test_wrong_login(user_details):
    # Set up WebDriver (ensure each thread has its own instance)
    driver = webdriver.Chrome()  # Or use any other driver like Firefox, Edge, etc.

    try:
        driver.get("https://saharassociation.cs.bgu.ac.il/test/")  # Replace with the actual URL

        # Fill in the login form
        account_number = driver.find_element(By.XPATH, "/html/body/div/div/div/div/div/form/div[1]/div/input")
        account_number.send_keys(user_details['account_number'])

        user_name = driver.find_element(By.XPATH, "/html/body/div/div/div/div/div/form/div[2]/div/input")
        user_name.send_keys(user_details['user_name'])

        password = driver.find_element(By.XPATH, "/html/body/div/div/div/div/div/form/div[3]/div/input")
        password.send_keys(user_details['password'])

        radio_but = driver.find_element(By.XPATH, "/html/body/div/div/div/div/div/form/div[4]/label[2]/span[1]/input")
        radio_but.click()

        connect = driver.find_element(By.XPATH, "/html/body/div/div/div/div/div/form/button")
        connect.click()

        time.sleep(5)  # Allow time for login to process


        nir = driver.find_element(By.XPATH, "//h4[contains(text(), 'שיחות פעילות')]")

        print(f"User {user_details['user_name']} logged in successfully.")
        # nir = driver.find_element(By.XPATH, "//p[contains(text(), 'הפרטים שסיפקת אינם נכונים.')]")

        # print(f"User {user_details['user_name']} didnt success to login as expected.")

    finally:
        driver.quit()  #


all_users = [
    {"account_number": "40920689", "user_name": "niryar", "password": "Omerhila1"},
    {"account_number": "40920689", "user_name": "omerdo", "password": "omerhila"},
    {"account_number": "40920689", "user_name": "ronfr", "password": "omerhila"},
    {"account_number": "40920689", "user_name": "hilaelb", "password": "omerhila"},
]


headers ={ 'Content-Type': 'application/json' }

json_file_path = 'test_case_risky_conv.json'

with open(json_file_path,'r') as f:
    data = json.load(f)
response = requests.post(url='http://localhost:6001/test/add_conversations', headers = headers, verify=False, json=data)

with ThreadPoolExecutor(max_workers=4) as executor:
    executor.map(login_test, all_users)  # Run login_test for each user in parallel


