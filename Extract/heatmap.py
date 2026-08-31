import os
import time
import requests
import pandas as pd

from dotenv import load_dotenv
from concurrent.futures import ThreadPoolExecutor, as_completed


# ============================================================
# CONFIGURATION
# ============================================================

load_dotenv()

API_KEY = os.getenv("FORTYGUARD_API_KEY")

if not API_KEY:
    raise ValueError(
        "FORTYGUARD_API_KEY not found in .env"
    )

BASE_URL = "https://api.fortyguard.com"

HEADERS = {
    "api-key": API_KEY,
    "Content-Type": "application/json"
}

INPUT_FILE = "Dataset/uscities.csv"
OUTPUT_FILE = "city_temperature.csv"


# ============================================================
# DATE RANGE
# ============================================================

START_DATE = "2024-04-01"
END_DATE = "2024-04-30"


# ============================================================
# CITY SELECTION
# ============================================================

# Select top 3,000 US cities by population
TOP_CITIES = 3000

# For testing:
# 0 = first city
# 5 = sixth city
START_CITY = 0

# Number of cities to process in this run
MAX_CITIES = 3000


# ============================================================
# PARALLEL PROCESSING
# ============================================================

# Number of city/date jobs running simultaneously.
#
# Start with 5.
# If stable, try 10.
#
MAX_WORKERS = 50


# ============================================================
# AOI
# ============================================================

DELTA_LAT = 0.0065
DELTA_LNG = 0.007


# ============================================================
# POLLING
# ============================================================

MAX_POLL_ATTEMPTS = 20
POLL_INTERVAL = 5


# ============================================================
# READ CITY DATA
# ============================================================

df = pd.read_csv(INPUT_FILE)


required_columns = [
    "city",
    "lat",
    "lng",
    "population"
]


for column in required_columns:

    if column not in df.columns:

        raise ValueError(
            f"Missing required column: {column}"
        )


# ============================================================
# CLEAN DATA
# ============================================================

df["population"] = pd.to_numeric(
    df["population"],
    errors="coerce"
)

df["lat"] = pd.to_numeric(
    df["lat"],
    errors="coerce"
)

df["lng"] = pd.to_numeric(
    df["lng"],
    errors="coerce"
)


df = df.dropna(
    subset=[
        "population",
        "lat",
        "lng"
    ]
)


# ============================================================
# SELECT TOP CITIES
# ============================================================

cities = (
    df
    .sort_values(
        by="population",
        ascending=False
    )
    .head(TOP_CITIES)
    .reset_index(drop=True)
)


print(
    f"Total valid cities: {len(df)}"
)

print(
    f"Selected top {len(cities)} cities"
)


# ============================================================
# CURRENT CITY BATCH
# ============================================================

cities_to_process = cities.iloc[
    START_CITY:
    START_CITY + MAX_CITIES
].copy()


print(
    f"Processing cities "
    f"{START_CITY + 1} to "
    f"{START_CITY + len(cities_to_process)}"
)


# ============================================================
# CREATE DAILY DATES
# ============================================================

dates = pd.date_range(
    start=START_DATE,
    end=END_DATE,
    freq="D"
)


dates = [
    date.strftime("%Y-%m-%d")
    for date in dates
]


print(
    f"Number of dates: {len(dates)}"
)

print(
    f"Expected API jobs: "
    f"{len(cities_to_process) * len(dates)}"
)


# ============================================================
# CREATE AOI
# ============================================================

def create_aoi(lat, lng):

    return [

        [
            lng - DELTA_LNG,
            lat - DELTA_LAT
        ],

        [
            lng + DELTA_LNG,
            lat - DELTA_LAT
        ],

        [
            lng + DELTA_LNG,
            lat + DELTA_LAT
        ],

        [
            lng - DELTA_LNG,
            lat + DELTA_LAT
        ],

        [
            lng - DELTA_LNG,
            lat - DELTA_LAT
        ]

    ]


# ============================================================
# TILE CENTER
# ============================================================

def get_tile_center(coordinates):

    # Remove duplicated closing point
    points = coordinates[:-1]

    if not points:
        return None, None

    avg_lng = sum(
        point[0]
        for point in points
    ) / len(points)

    avg_lat = sum(
        point[1]
        for point in points
    ) / len(points)

    return avg_lat, avg_lng


# ============================================================
# DISTANCE
# ============================================================

def distance_squared(
    lat1,
    lng1,
    lat2,
    lng2
):

    return (
        (lat1 - lat2) ** 2
        +
        (lng1 - lng2) ** 2
    )


# ============================================================
# FIND CENTER TILE
# ============================================================

def find_center_tile(
    features,
    city_lat,
    city_lng
):

    best_tile = None

    best_distance = float("inf")


    for feature in features:

        geometry = feature.get(
            "geometry"
        )

        if not geometry:
            continue


        coordinates = geometry.get(
            "coordinates"
        )

        if not coordinates:
            continue


        # Polygon → first ring
        polygon = coordinates[0]


        tile_lat, tile_lng = (
            get_tile_center(polygon)
        )


        if tile_lat is None:
            continue


        distance = distance_squared(
            city_lat,
            city_lng,
            tile_lat,
            tile_lng
        )


        if distance < best_distance:

            best_distance = distance

            best_tile = {

                "feature": feature,

                "tile_lat": tile_lat,

                "tile_lng": tile_lng

            }


    return best_tile


# ============================================================
# PROCESS ONE CITY + ONE DATE
# ============================================================

def process_city_date(
    position,
    row,
    date
):

    city = row["city"]

    city_lat = float(row["lat"])

    city_lng = float(row["lng"])

    population = int(
        row["population"]
    )


    print(
        f"[City {position + 1}] "
        f"{city} | {date} | submitting"
    )


    # ========================================================
    # CREATE AOI
    # ========================================================

    coordinates = create_aoi(
        city_lat,
        city_lng
    )


    # ========================================================
    # PAYLOAD
    #
    # IMPORTANT:
    # We use the SAME date for start and end.
    #
    # This gives us one observation for this specific date.
    # ========================================================

    payload = {

        "polygon_aoi": {

            "type": "FeatureCollection",

            "features": [

                {

                    "type": "Feature",

                    "properties": {},

                    "geometry": {

                        "type": "Polygon",

                        "coordinates": [
                            coordinates
                        ]

                    }

                }

            ]

        },

        "date_time": {

            "start_date": date,

            "end_date": date,

            "filter_type": 4

        },

        "granularity": 80

    }


    # ========================================================
    # SUBMIT HEATMAP
    # ========================================================

    try:

        response = requests.post(

            f"{BASE_URL}/v1/heatmap",

            headers=HEADERS,

            json=payload,

            timeout=30

        )

    except requests.RequestException as e:

        return {

            "success": False,

            "city": city,

            "date": date,

            "error": f"Submit error: {e}"

        }


    if response.status_code != 200:

        return {

            "success": False,

            "city": city,

            "date": date,

            "error": (
                f"HTTP {response.status_code}: "
                f"{response.text}"
            )

        }


    # ========================================================
    # GET ACTIVITY ID
    # ========================================================

    try:

        data = response.json()

        activity_id = (
            data["data"]["activity_id"]
        )

    except Exception as e:

        return {

            "success": False,

            "city": city,

            "date": date,

            "error": (
                f"Invalid API response: {e}"
            )

        }


    print(
        f"[City {position + 1}] "
        f"{city} | {date} | "
        f"Activity: {activity_id}"
    )


    # ========================================================
    # POLL STATUS
    # ========================================================

    status_url = (
        f"{BASE_URL}/v1/status/"
        f"{activity_id}"
    )


    completed_result = None


    for attempt in range(
        MAX_POLL_ATTEMPTS
    ):

        try:

            response = requests.get(

                status_url,

                headers={
                    "api-key": API_KEY
                },

                timeout=30

            )

            response.raise_for_status()


            status_data = (
                response.json()["data"]
            )


            status = status_data.get(
                "status"
            )


        except requests.RequestException as e:

            print(
                f"{city} | {date} | "
                f"Status error: {e}"
            )

            time.sleep(
                POLL_INTERVAL
            )

            continue


        if status == "Completed":

            completed_result = (
                status_data.get("result")
            )

            break


        if status == "Failed":

            return {

                "success": False,

                "city": city,

                "date": date,

                "error": (
                    f"Heatmap failed. "
                    f"Activity: {activity_id}"
                )

            }


        time.sleep(
            POLL_INTERVAL
        )


    # ========================================================
    # TIMEOUT
    # ========================================================

    if not completed_result:

        return {

            "success": False,

            "city": city,

            "date": date,

            "error": (
                "Heatmap timed out"
            )

        }


    # ========================================================
    # MAP DATA
    # ========================================================

    map_data = (
        completed_result.get(
            "map_data"
        )
    )


    if not map_data:

        return {

            "success": False,

            "city": city,

            "date": date,

            "error": "No map_data returned"

        }


    features = map_data.get(
        "features",
        []
    )


    if not features:

        return {

            "success": False,

            "city": city,

            "date": date,

            "error": "No tiles returned"

        }


    # ========================================================
    # FIND CENTER TILE
    # ========================================================

    center_tile = find_center_tile(

        features,

        city_lat,

        city_lng

    )


    if not center_tile:

        return {

            "success": False,

            "city": city,

            "date": date,

            "error": (
                "Center tile not found"
            )

        }


    feature = center_tile[
        "feature"
    ]


    properties = feature.get(
        "properties",
        {}
    )


    # ========================================================
    # TEMPERATURE DATA
    # ========================================================

    tile_id = properties.get(
        "tile_id"
    )


    average_temperature = (
        properties.get(
            "average_temperature"
        )
    )


    min_temperature = (
        properties.get(
            "min_temperature"
        )
    )


    max_temperature = (
        properties.get(
            "max_temperature"
        )
    )


    tile_lat = center_tile[
        "tile_lat"
    ]


    tile_lng = center_tile[
        "tile_lng"
    ]


    # ========================================================
    # RESULT
    # ========================================================

    result = {

        "city": city,

        "city_lat": city_lat,

        "city_lng": city_lng,

        "population": population,

        "tile_id": tile_id,

        "tile_lat": tile_lat,

        "tile_lng": tile_lng,

        "average_temperature": (
            average_temperature
        ),

        "min_temperature": (
            min_temperature
        ),

        "max_temperature": (
            max_temperature
        ),

        "date": date

    }


    print(
        f"[City {position + 1}] "
        f"{city} | {date} | "
        f"COMPLETED | "
        f"Avg: {average_temperature} °C"
    )


    return {

        "success": True,

        "city": city,

        "date": date,

        "result": result

    }


# ============================================================
# CREATE ALL CITY × DATE JOBS
# ============================================================

jobs = []


for position, row in cities_to_process.iterrows():

    for date in dates:

        jobs.append(
            (
                position,
                row,
                date
            )
        )


print(
    f"\nTotal jobs created: {len(jobs)}"
)


# ============================================================
# LOAD EXISTING OUTPUT
# ============================================================

if os.path.exists(
    OUTPUT_FILE
):

    existing_df = pd.read_csv(
        OUTPUT_FILE
    )

    print(
        f"Existing rows: "
        f"{len(existing_df)}"
    )

else:

    existing_df = pd.DataFrame()


# ============================================================
# RESUME SUPPORT
# ============================================================

if not existing_df.empty:

    completed_keys = set(

        zip(

            existing_df["city"].astype(str),

            existing_df["date"].astype(str)

        )

    )


    remaining_jobs = []

    for position, row, date in jobs:

        key = (
            str(row["city"]),
            str(date)
        )

        if key not in completed_keys:

            remaining_jobs.append(
                (
                    position,
                    row,
                    date
                )
            )


    jobs = remaining_jobs


    print(
        f"Remaining jobs: "
        f"{len(jobs)}"
    )


# ============================================================
# PARALLEL EXECUTION
# ============================================================

new_results = []


with ThreadPoolExecutor(
    max_workers=MAX_WORKERS
) as executor:


    future_to_job = {}


    for position, row, date in jobs:

        future = executor.submit(

            process_city_date,

            position,

            row,

            date

        )

        future_to_job[future] = (
            position,
            row["city"],
            date
        )


    completed_count = 0


    for future in as_completed(
        future_to_job
    ):

        position, city, date = (
            future_to_job[future]
        )


        try:

            result = future.result()


        except Exception as e:

            print(
                f"\nERROR: "
                f"{city} | {date}"
            )

            print(e)

            continue


        if not result["success"]:

            print(
                f"\nFAILED: "
                f"{city} | {date}"
            )

            print(
                result["error"]
            )

            continue


        # ====================================================
        # ADD RESULT
        # ====================================================

        new_results.append(
            result["result"]
        )


        completed_count += 1


        # ====================================================
        # SAVE PROGRESS
        # ====================================================

        new_df = pd.DataFrame(
            new_results
        )


        if existing_df.empty:

            combined_df = new_df

        else:

            combined_df = pd.concat(

                [
                    existing_df,
                    new_df
                ],

                ignore_index=True

            )


        combined_df = (
            combined_df
            .drop_duplicates(

                subset=[
                    "city",
                    "date"
                ],

                keep="last"

            )
        )


        combined_df.to_csv(

            OUTPUT_FILE,

            index=False

        )


        print(
            f"\nPROGRESS: "
            f"{completed_count}/"
            f"{len(jobs)} "
            f"new observations saved"
        )


# ============================================================
# FINAL SUMMARY
# ============================================================

if os.path.exists(
    OUTPUT_FILE
):

    final_df = pd.read_csv(
        OUTPUT_FILE
    )


    print(
        "\n"
        + "=" * 70
    )

    print(
        "PROCESSING COMPLETE"
    )

    print(
        f"Total rows: "
        f"{len(final_df)}"
    )

    print(
        f"Unique cities: "
        f"{final_df['city'].nunique()}"
    )

    print(
        f"Unique dates: "
        f"{final_df['date'].nunique()}"
    )

    print(
        f"Output: "
        f"{OUTPUT_FILE}"
    )

    print(
        "=" * 70
    )