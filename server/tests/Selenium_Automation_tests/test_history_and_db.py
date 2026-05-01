import json
import time
from datetime import datetime, timedelta, timezone
from selenium.webdriver.common.keys import Keys

# Global variables to store conversation IDs for each time range
import json
from datetime import datetime, timedelta, timezone
import random

import requests
from selenium.webdriver.chrome import webdriver
from selenium import webdriver
from selenium.webdriver.common.by import By
from concurrent.futures import ThreadPoolExecutor

# Global variables to store conversation IDs for each time range
last_10_min_conv_ids = []
min_20_50_conv_ids = []
min_70_110_conv_ids = []
min_130_230_conv_ids = []


def login_and_look_for_consumers_by_timestamp(user_details):
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

    time.sleep(3)
    burger_icon = driver.find_element(By.XPATH, "/html/body/div[1]/div/div/div/button")
    burger_icon.click()

    time.sleep(2)
    conv_history = driver.find_element(By.XPATH,"/html/body/div/div/div/div/div[1]/button[3]")
    conv_history.click()

    time.sleep(2)

    list_choose = driver.find_element(By.XPATH,"/html/body/div/div/div/div/div/div[2]/div/div/div")
    print("before list chose click")
    list_choose.click()
    print("after list chose click")

    # time.sleep(1)
    choose_15_min = driver.find_element(By.XPATH,"/html/body/div[2]/div[3]/ul/li[1]")
    choose_15_min.click()

    filter_by = driver.find_element(By.XPATH, "/html/body/div/div/div/div/div/div[3]/div/div/input")
    filter_by.send_keys(last_10_min_conv_ids[0])
    driver.find_element(By.XPATH, "/html/body/div/div/div/div/div/div[4]/div/div[2]/div/div[4]/p") # verify it appear, else exception is thrown
    try:
        filter_by.send_keys(Keys.CONTROL + "a")  # Select all text
        filter_by.send_keys(Keys.BACKSPACE)  # Clear text
        filter_by.send_keys(min_20_50_conv_ids[0])
        driver.find_element(By.XPATH,
                            "/html/body/div/div/div/div/div/div[4]/div/div[2]/div/div[4]/p")  # verify it appear, else exception is thrown
        raise Exception("should not appear")
    except Exception as e:
        if str(e) == 'should not appear':
            raise Exception("should not appear")
        print("not found as expected")

    list_choose.click()
    time.sleep(2)
    choose_1hour= driver.find_element(By.XPATH, "/html/body/div[2]/div[3]/ul/li[3]")
    print("nir")
    choose_1hour.click()
    print("nir2")
    filter_by.send_keys(Keys.CONTROL + "a")  # Select all text
    filter_by.send_keys(Keys.BACKSPACE)  # Clear text
    filter_by.send_keys(min_20_50_conv_ids[0])
    driver.find_element(By.XPATH, "/html/body/div/div/div/div/div/div[4]/div/div[2]/div/div[4]/p") # verify it appear, else exception is thrown

    try:
        filter_by.send_keys(Keys.CONTROL + "a")  # Select all text
        filter_by.send_keys(Keys.BACKSPACE)  # Clear text
        filter_by.send_keys(min_70_110_conv_ids[0])
        driver.find_element(By.XPATH,
                            "/html/body/div/div/div/div/div/div[4]/div/div[2]/div/div[4]/p")  # verify it appear, else exception is thrown
        raise Exception("should not appear")
    except Exception as e:
        if str(e) == 'should not appear':
            raise Exception("should not appear")
        print("not found as expected")

    list_choose.click()

    choose_4hour= driver.find_element(By.XPATH, "/html/body/div[2]/div[3]/ul/li[5]")
    choose_4hour.click()
    filter_by.send_keys(Keys.CONTROL + "a")  # Select all text
    filter_by.send_keys(Keys.BACKSPACE)  # Clear text
    filter_by.send_keys(last_10_min_conv_ids[0])
    driver.find_element(By.XPATH, "/html/body/div/div/div/div/div/div[4]/div/div[2]/div/div[4]/p") # verify it appear, else exception is thrown

    filter_by.send_keys(Keys.CONTROL + "a")  # Select all text
    filter_by.send_keys(Keys.BACKSPACE)  # Clear text
    filter_by.send_keys(min_20_50_conv_ids[0])
    driver.find_element(By.XPATH, "/html/body/div/div/div/div/div/div[4]/div/div[2]/div/div[4]/p") # verify it appear, else exception is thrown

    filter_by.send_keys(Keys.CONTROL + "a")  # Select all text
    filter_by.send_keys(Keys.BACKSPACE)  # Clear text
    filter_by.send_keys(min_70_110_conv_ids[0])
    driver.find_element(By.XPATH, "/html/body/div/div/div/div/div/div[4]/div/div[2]/div/div[4]/p") # verify it appear, else exception is thrown

    filter_by.send_keys(Keys.CONTROL + "a")  # Select all text
    filter_by.send_keys(Keys.BACKSPACE)  # Clear text
    filter_by.send_keys(min_130_230_conv_ids[0])
    driver.find_element(By.XPATH, "/html/body/div/div/div/div/div/div[4]/div/div[2]/div/div[4]/p") # verify it appear, else exception is thrown

    driver.quit()

    #Kill the server
    #start the server
    #wait 1minute
    #Login and verify anything

def process_conversation_data(data):
    """
    Processes conversation data, renaming consumer names, adjusting timestamps,
    distributing conversations across specified time ranges, and saving conversation IDs.
    """
    global last_10_min_conv_ids, min_20_50_conv_ids, min_70_110_conv_ids, min_130_230_conv_ids

    if not data or "conversationHistoryRecords" not in data:
        return data

    records = data["conversationHistoryRecords"]
    records = records[:30]
    records = distribute_conversations(records) #distribute conversations

    data["conversationHistoryRecords"] = records #replace the records with the distributed ones

    if len(records) > 30:
        if "_metadata" in data:
            data["_metadata"]["count"] = 30
    elif "_metadata" in data:
        data["_metadata"]["count"] = len(records)

    for record in records:
        if "consumerParticipants" in record:
            for j, participant in enumerate(record["consumerParticipants"]):
                if "consumerName" in participant:
                    participant["consumerName"] = f"consumer{records.index(record) + 1}"

        if "info" in record:
            record["info"] = adjust_timestamps(record["info"])

        if "messageRecords" in record:
            for message in record["messageRecords"]:
                if "time" in message and "timeL" in message:
                    message["time"], message["timeL"] = adjust_single_timestamp(message["time"], message["timeL"])

        if "consumerParticipants" in record:
            for participant in record["consumerParticipants"]:
                if "time" in participant and "timeL" in participant:
                    participant["time"], participant["timeL"] = adjust_single_timestamp(participant["time"], participant["timeL"])
                if "joinTime" in participant and "joinTimeL" in participant:
                    participant["joinTime"], participant["joinTimeL"] = adjust_single_timestamp(participant["joinTime"], participant["joinTimeL"])

    return data

def distribute_conversations(records):
    """Distributes conversations across specified time ranges and saves conversation IDs."""
    global last_10_min_conv_ids, min_20_50_conv_ids, min_70_110_conv_ids, min_130_230_conv_ids

    now = datetime.now(timezone.utc)
    print("datetime is ", now)
    last_10_min = []
    min_20_50 = []
    min_70_110 = []
    min_130_230 = []

    for i, record in enumerate(records):
        if "info" in record and "conversationId" in record["info"]:
            if i < 5:
                # Last 10 minutes
                minutes_ago = random.uniform(0, 8)
                new_time = now - timedelta(minutes=minutes_ago)
                last_10_min.append(record)
                last_10_min_conv_ids.append(record["info"]["conversationId"])
            elif i < 10:
                # 20-50 minutes ago
                minutes_ago = random.uniform(20, 50)
                new_time = now - timedelta(minutes=minutes_ago)
                min_20_50.append(record)
                min_20_50_conv_ids.append(record["info"]["conversationId"])
            elif i < 20:
                # 70-110 minutes ago
                minutes_ago = random.uniform(70, 110)
                new_time = now - timedelta(minutes=minutes_ago)
                min_70_110.append(record)
                min_70_110_conv_ids.append(record["info"]["conversationId"])
            else:
                # 130-230 minutes ago
                minutes_ago = random.uniform(130, 230)
                new_time = now - timedelta(minutes=minutes_ago)
                min_130_230.append(record)
                min_130_230_conv_ids.append(record["info"]["conversationId"])
            record["info"]["startTime"] = new_time.isoformat().replace('+00:00', '+0000')
            record["info"]["startTimeL"] = int(new_time.timestamp() * 1000)
            record["info"]["endTime"] = new_time.isoformat().replace('+00:00', '+0000')
            record["info"]["endTimeL"] = int(new_time.timestamp() * 1000)
            record["info"]["conversationEndTime"] = new_time.isoformat().replace('+00:00', '+0000')
            record["info"]["conversationEndTimeL"] = int(new_time.timestamp() * 1000)
            now_n = datetime.now(timezone.utc)
            now_ms = int(now_n.timestamp() * 1000)
            print( (now_ms - int(record["info"]["endTimeL"]))/60000)

    result = (
        last_10_min
        + min_20_50
        + min_70_110
        + min_130_230
    )
    return result


def adjust_timestamps(info):
    """
    Adjusts all timestamps within the 'info' dictionary to be within the last 2 hours.

    Args:
        info (dict): The 'info' dictionary containing timestamp data.

    Returns:
        dict: The modified 'info' dictionary with adjusted timestamps.
    """
    now = datetime.now(timezone.utc)
    two_hours_ago = now - timedelta(hours=2)

    for key, value in info.items():
        if key.endswith("Time"):  # Check if the key ends with "Time"
            try:
                dt = datetime.fromisoformat(value.replace('Z', '+00:00'))
                if dt < two_hours_ago:
                    diff = two_hours_ago - dt
                    new_dt = now - diff
                    new_time_str = new_dt.isoformat().replace('+00:00', '+0000')
                    info[key] = new_time_str
                    if key + "L" in info:
                        info[key + "L"] = int(new_dt.timestamp() * 1000)
            except ValueError:
                pass # if the time format is wrong, skip it.

        if key.endswith("TimeL"):
            try:
                original_time = datetime.fromtimestamp(value/1000, tz=timezone.utc)
                if original_time < two_hours_ago:
                    diff = two_hours_ago - original_time
                    new_dt = now - diff
                    info[key] = int(new_dt.timestamp() * 1000)
            except (TypeError, ValueError):
                pass
    return info

def adjust_single_timestamp(time_str, time_l):
    """
    Adjusts a single timestamp to be within the last 2 hours.

    Args:
        time_str (str): The timestamp string.
        time_l (int): The timestamp in milliseconds.

    Returns:
        tuple: The adjusted timestamp string and milliseconds.
    """
    now = datetime.now(timezone.utc)
    two_hours_ago = now - timedelta(hours=2)

    try:
        dt = datetime.fromisoformat(time_str.replace('Z', '+00:00'))
        if dt < two_hours_ago:
            diff = two_hours_ago - dt
            new_dt = now - diff
            new_time_str = new_dt.isoformat().replace('+00:00', '+0000')
            new_time_l = int(new_dt.timestamp() * 1000)
            return new_time_str, new_time_l
    except ValueError:
        pass
    return time_str, time_l

def main():
    """Reads JSON, processes, and writes modified data."""
    global last_10_min_conv_ids, min_20_50_conv_ids, min_70_110_conv_ids, min_130_230_conv_ids

    input_file = "closed_conversation.json"
    output_file = "closed_output.json"

    try:
        with open(input_file, "r", encoding="utf-8") as f:
            data = json.load(f)

        modified_data = process_conversation_data(data)

        headers = {'Content-Type': 'application/json'}

        response = requests.post(url='http://localhost:6001/test/add_closed_conversations', headers=headers,
                                 verify=False,
                                 json=modified_data)
        # start_time = time.time()

        time.sleep(20)

        users = [
            {"account_number": "40920689", "user_name": "niryar", "password": "Omerhila1"},
            {"account_number": "40920689", "user_name": "omerdo", "password": "omerhila"},
            {"account_number": "40920689", "user_name": "ronfr", "password": "omerhila"},
            {"account_number": "40920689", "user_name": "hilaelb", "password": "omerhila"},
            {"account_number": "40920689", "user_name": "sel1", "password": "omerhila"},
            {"account_number": "40920689", "user_name": "sel2", "password": "omerhila"},
            {"account_number": "40920689", "user_name": "sel3", "password": "omerhila"},
            {"account_number": "40920689", "user_name": "sel4", "password": "omerhila"},
            {"account_number": "40920689", "user_name": "sel5", "password": "omerhila"},
            {"account_number": "40920689", "user_name": "sel6", "password": "omerhila"}
        ]

        # login_and_look_for_consumers_by_timestamp(users[0])
        with ThreadPoolExecutor(max_workers=10) as executor:
            executor.map(login_and_look_for_consumers_by_timestamp, users)
        print(response.status_code)

        print(f"Processed data written to {output_file}")
        print(f"Last 10 min conversation IDs: {last_10_min_conv_ids}")
        print(f"20-50 min ago conversation IDs: {min_20_50_conv_ids}")
        print(f"70-110 min ago conversation IDs: {min_70_110_conv_ids}")
        print(f"130-230 min ago conversation IDs: {min_130_230_conv_ids}")

    except FileNotFoundError:
        print(f"Error: Input file '{input_file}' not found.")
    except json.JSONDecodeError:
        print(f"Error: Invalid JSON in '{input_file}'.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

if __name__ == "__main__":
    main()
