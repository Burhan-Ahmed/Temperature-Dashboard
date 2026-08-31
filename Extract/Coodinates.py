import requests
import pandas as pd
import time


INPUT_FILE = "Dataset/uscities.csv"
OUTPUT_FILE = "usa_cities_geocoded.xlsx"

NOMINATIM_URL = "https://nominatim.openstreetmap.org/search"

HEADERS = {
    "User-Agent": "my-heat-analytics-project/1.0"
}


# Read dataset
df = pd.read_csv(INPUT_FILE)

# Check columns
required_columns = [
    "city_ascii",
    "state_name",
    "lat",
    "lng"
]

for column in required_columns:
    if column not in df.columns:
        raise ValueError(f"Missing column: {column}")


# --------------------------------------------------
# START FROM THIS INDEX
# --------------------------------------------------

START_INDEX = 18000

# Change this to the index AFTER Ellenville
# Example:
# START_INDEX = 1234


# --------------------------------------------------
# GEOCODING
# --------------------------------------------------

for index in range(START_INDEX, len(df)):

    row = df.iloc[index]

    city = row["city_ascii"]
    state = row["state_name"]

    query = f"{city}, {state}, USA"

    params = {
        "q": query,
        "format": "jsonv2",
        "limit": 1
    }

    try:

        response = requests.get(
            NOMINATIM_URL,
            params=params,
            headers=HEADERS,
            timeout=30
        )

        response.raise_for_status()

        results = response.json()

        if results:

            latitude = float(results[0]["lat"])
            longitude = float(results[0]["lon"])

            # Replace coordinates
            df.at[index, "lat"] = latitude
            df.at[index, "lng"] = longitude

            print(
                f"INDEX {index} | "
                f"{city}, {state} → "
                f"{latitude}, {longitude}"
            )

        else:

            print(
                f"INDEX {index} | "
                f"NOT FOUND: {city}, {state}"
            )

    except Exception as e:

        print(
            f"INDEX {index} | "
            f"ERROR: {city}, {state} → {e}"
        )

    # Nominatim public API rate limit
    #time.sleep(1)


# Save
df.to_excel(
    OUTPUT_FILE,
    index=False
)

print("\nCompleted!")
print(f"Saved to: {OUTPUT_FILE}")