import subprocess
import time
import requests
import os
import signal

SERVICE_NAME = "sahar_testing.service"
LOGIN_URL = "http://127.0.0.1:6001/login"

def get_gunicorn_pid():
    try:
        output = subprocess.check_output(["ps", "aux"])
        lines = output.decode().splitlines()
        for line in lines:
            if "gunicorn" in line and "server:app" in line:
                return int(line.split()[1])  # second column is PID
        return None
    except subprocess.CalledProcessError:
        return None

def kill_gunicorn():
    pid = get_gunicorn_pid()
    if pid:
        print(f"Killing Gunicorn PID {pid}")
        os.kill(pid, signal.SIGKILL)
        time.sleep(2)
        return True
    print("Gunicorn not running")
    return False

def is_service_active():
    try:
        output = subprocess.check_output(["systemctl", "is-active", SERVICE_NAME])
        return output.decode().strip() == "active"
    except subprocess.CalledProcessError:
        return False

def wait_for_server(timeout=20):
    print("Waiting for server to come back via /login...")
    payload = {
        "account_id": "40920689",
        "username": "hilaelb",
        "password": "omerhila"
    }
    headers = {
        "Content-Type": "application/json"
    }

    for _ in range(timeout):
        try:
            response = requests.post(LOGIN_URL, json=payload, headers=headers, timeout=2)
            if response.ok:
                print("Server is back up! ✅")
                return True
        except requests.RequestException:
            pass
        time.sleep(1)

    print("Server did not recover in time. ❌")
    return False

def test_server_recovery():
    print("🔁 Starting test: crash and recovery")

    subprocess.run(["sudo", "systemctl", "start", SERVICE_NAME])
    time.sleep(5)

    assert is_service_active(), "❌ Service is not active before crash"

    assert kill_gunicorn(), "❌ Failed to kill Gunicorn"

    time.sleep(7)

    assert is_service_active(), "❌ Service did not restart"

    assert wait_for_server(), "❌ Server did not recover at HTTP level"

    print("✅ Server recovery test passed!")


def test_multiple_crashes():
    print("🔁 Starting test: multiple crashes")

    subprocess.run(["sudo", "systemctl", "start", SERVICE_NAME])
    time.sleep(5)

    for i in range(3):
        print(f"Crash attempt #{i+1}")
        assert kill_gunicorn(), f"❌ Failed to kill Gunicorn on attempt #{i+1}"
        time.sleep(9)
        assert is_service_active(), f"❌ Service did not restart after crash #{i+1}"
        assert wait_for_server(), f"❌ Server did not recover after crash #{i+1}"

    print("✅ Multiple crash recovery test passed!")
if __name__ == "__main__":
    test_server_recovery()
    test_multiple_crashes()
