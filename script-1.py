import requests
import csv
import time

wallet_address = "0x56687bf447db6ffa42ffe2204a05edaa20f55839"
base_url = "https://clob.polymarket.com/api/v0/fills"
limit = 100  # Max allowed by API
all_fills = []
page = 1

try:
    while True:
        params = {
            "userAddress": wallet_address,
            "limit": limit,
            "page": page
        }
        resp = requests.get(base_url, params=params)
        resp.raise_for_status()  # Raises HTTPError for bad responses
        fills = resp.json()
        if not fills:
            break
        all_fills.extend(fills)
        print(f"Fetched page {page} with {len(fills)} fills")
        page += 1
        time.sleep(0.2)  # Be polite to the API

    if all_fills:
        # Collect all unique field names
        fieldnames = set()
        for fill in all_fills:
            fieldnames.update(fill.keys())
        fieldnames = list(fieldnames)
        # Save to CSV
        filename = f"{wallet_address}_clob_fills.csv"
        with open(filename, "w", newline='', encoding="utf-8") as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            for fill in all_fills:
                writer.writerow(fill)
        print(f"Saved {len(all_fills)} fills to {filename}")
    else:
        print("No fills found for this user.")
except requests.exceptions.RequestException as e:
    print(f"Error fetching data from API: {e}")
except Exception as e:
    print(f"An error occurred: {e}")
