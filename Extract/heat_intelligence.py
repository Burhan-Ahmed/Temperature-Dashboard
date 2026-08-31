import os
import time
from dotenv import load_dotenv
import requests

load_dotenv()

BASE_URL = "https://api.fortyguard.com"
API_KEY = os.getenv("FORTYGUARD_API_KEY")

if not API_KEY:
    raise ValueError("FORTYGUARD_API_KEY environment variable is not set")


# Headers
headers = {
    "api-key": API_KEY,
    "Content-Type": "application/json"
}


# Heat Intelligence request
payload = {
    "latitude": 33.4484,
    "longitude": -112.0740,
    "temperature": 44.44,
    "date": "2024-04-22",
    "analysis": [
        "environmental"
    ]
}


# --------------------------------------------------
# 1. Submit Heat Intelligence task
# --------------------------------------------------

print("Submitting Heat Intelligence request...")

response = requests.post(
    f"{BASE_URL}/v1/heat_intelligence",
    headers=headers,
    json=payload,
    timeout=30
)

print("Submit status:", response.status_code)
print("Submit response:", response.text)

response.raise_for_status()

data = response.json()

activity_id = data["data"]["activity_id"]

print("\nActivity ID:", activity_id)


# --------------------------------------------------
# 2. Check task status
# --------------------------------------------------

status_url = f"{BASE_URL}/v1/status/{activity_id}"

while True:

    response = requests.get(
        status_url,
        headers={
            "api-key": API_KEY
        },
        timeout=30
    )

    print("\nStatus HTTP:", response.status_code)

    response.raise_for_status()

    result = response.json()

    print("Status response:", result)

    status = result["data"]["status"]

    print("Current status:", status)

    # Task completed
    if status == "Completed":
        print("\nTask completed successfully!")
        break

    # Task failed
    if status == "Failed":
        print("\nTask failed!")
        break

    # Still processing
    print("Still processing... waiting 5 seconds.")
    time.sleep(5)