import threading
import time
from concurrent.futures import ThreadPoolExecutor
from selenium import webdriver
from selenium.webdriver.common.by import By
import requests
import json
conversation_id = []
start_time = None
results = []
drivers = []
NUM_USERS = 4
# Insert conversation to backend
def post_conversation():
    global conversation_id, start_time
    headers = {'Content-Type': 'application/json'}

    json_file_path = 'test_no_risky_conv.json'

    with open(json_file_path, 'r') as f:
        data = json.load(f)
    response = requests.post(url='http://localhost:6001/test/add_conversations', headers=headers, verify=False,
                             json=data)
    start_time = time.time()

    print(response.status_code)
    conversation_id = [ "d0cfcc2d-161d-47b3-9908-336477d5f4a8", "51bead29-3449-41ef-8c3c-ee1b4b6776c2", "10b60697-d913-433d-bd12-50a648616938",
                         "a6b6ba42-15f5-49cd-8f7f-78cbc5e90e58", "b29b0c75-f7d1-45b4-9043-086e119d1346"]


# Function to perform the login test for each user
def login_user(user_details, user_index):
    # Set up WebDriver (ensure each thread has its own instance)
    driver = webdriver.Chrome()  # Or use any other driver like Firefox, Edge, etc.

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

    time.sleep(2)
    drivers.append((user_index, driver))



def wait_for_conversation(user_index, driver):
    global results
    global start_time
    max_wait = 60
    poll_interval = 1
    elapsed = 2

    time.sleep(2)
    filter_by_id = driver.find_element(By.XPATH, "/html/body/div/div/div/div/div/div[2]/div/div/input")
    filter_by_id.send_keys(conversation_id[3])

    while elapsed < max_wait:
        try:
            driver.find_element(By.XPATH, "/html/body/div/div/div/div/div/div[3]/div/div[2]/div/div[4]/p")
            duration = time.time() - start_time
            results.append((user_index, duration))
            return
        except Exception as e:
            time.sleep(poll_interval)
            elapsed+=poll_interval
    results.append((user_index,None))


def run_test():
    print("Logging all users")
    login_threads = []
    users = [
        {"account_number": "40920689", "user_name": "niryar", "password": "Omerhila1"},
        {"account_number": "40920689", "user_name": "omerdo", "password": "omerhila"},
        {"account_number": "40920689", "user_name": "ronfr", "password": "omerhila"},
        {"account_number": "40920689", "user_name": "hilaelb", "password": "omerhila"},
        # {"account_number": "40920689", "user_name": "sel1", "password": "omerhila"},
        # {"account_number": "40920689", "user_name": "sel2", "password": "omerhila"},
        # {"account_number": "40920689", "user_name": "sel3", "password": "omerhila"},
        # {"account_number": "40920689", "user_name": "sel4", "password": "omerhila"},
        # {"account_number": "40920689", "user_name": "sel5", "password": "omerhila"},
        # {"account_number": "40920689", "user_name": "sel6", "password": "omerhila"}

    ]
    for i in range(NUM_USERS):
        t = threading.Thread(target=login_user,args=(users[i],i))
        login_threads.append(t)
        t.start()

    for t in login_threads:
        t.join()

    post_conversation()

    check_threads = []
    for user_index, driver in drivers:
        t = threading.Thread(target=wait_for_conversation,args=(user_index ,driver))
        check_threads.append(t)
        t.start()

    for t in check_threads:
        t.join()

    print("\nResults:")
    for user_index, duration in sorted(results):
        if duration is not None:
            print(f"User {user_index}: Conversation appeared after {duration:.2f}s")
        else:
            print(f"User {user_index}: Did not see the conversation in time")

    # Cleanup
    for _, driver in drivers:
        driver.quit()

if __name__ == "__main__":
    run_test()



