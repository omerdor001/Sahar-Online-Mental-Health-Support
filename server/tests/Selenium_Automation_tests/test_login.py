import time
from concurrent.futures import ThreadPoolExecutor
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.options import Options
# Function to perform the login test for each user
def login_test(user_details):
    # Set up WebDriver (ensure each thread has its own instance)
    driver = webdriver.Chrome()  # Or use any other driver like Firefox, Edge, etc.

    try:
        driver.get("https://saharassociation.cs.bgu.ac.il/test")  # Replace with the actual URL

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

        time.sleep(30)  # Allow time for login to process

        nir = driver.find_element(By.XPATH, "//h4[contains(text(), 'שיחות פעילות')]")

        print(f"User {user_details['user_name']} logged in successfully.")

    finally:
        driver.quit()  # Ensure the WebDriver instance is closed properly

user_details = {"account_number": "40920689", "user_name": "niryar", "password": "Omerhila1"}

login_test(user_details)
