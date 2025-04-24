import os
import json
from py_clob_client.client import ClobClient
from py_clob_client.constants import POLYGON
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

def main():
    private_key = os.getenv("POLYMARKET_PRIVATE_KEY")
    if not private_key:
        raise ValueError("Missing POLYMARKET_PRIVATE_KEY in .env")

    print(f"[DEBUG] Using private key: {private_key[:6]}...")

    client = ClobClient(
        host="https://clob.polymarket.com",
        key=private_key,
        chain_id=POLYGON
    )
    api_creds = client.create_or_derive_api_creds()
    client.set_api_creds(api_creds)

    markets = []
    next_cursor = ""  # Start with ""
    checked_cursors_log = "checked_cursors.log"
    timestamp_format = "%Y-%m-%d %H:%M:%S"

    while len(markets) < 100:
        print(f"[DEBUG] Fetching markets with next_cursor: {next_cursor!r}")
        try:
            response = client.get_markets(next_cursor=next_cursor)

            print(f"[DEBUG] Raw response keys: {list(response.keys())}")

            if 'data' in response:
                print(f"[DEBUG] Number of markets in this page: {len(response['data'])}")
                # Filter for open markets where closed is False and active is True
                filtered_markets = [market for market in response['data'] if not market.get("closed", True) and market.get("active", False)]
                markets.extend(filtered_markets)
            else:
                print("[DEBUG] No 'data' key in response, full response:", json.dumps(response, indent=2))
                break

            next_cursor = response.get("next_cursor")
            print(f"[DEBUG] Next cursor received: {next_cursor!r}")

            # End of pagination: next_cursor is None or 'LTE=' (per docs[2])
            if not next_cursor or next_cursor == "LTE=":
                print("[DEBUG] No more pages to fetch or end cursor received.")
                break

        except Exception as e:
            print(f"[ERROR] Exception during API call: {e}")
            break

    # Add timestamp to markets
    timestamp = datetime.now().strftime(timestamp_format)
    markets_with_timestamp = {"timestamp": timestamp, "markets": markets[:100]}

    # Export to JSON file with timestamp
    output_file = f"open_markets_{timestamp}.json"
    with open(output_file, 'w') as f:
        json.dump(markets_with_timestamp, f, indent=4)
        print(f"[INFO] Markets have been saved to {output_file}")

    # Log checked cursors
    if next_cursor and next_cursor != "LTE=":
        with open(checked_cursors_log, 'a') as log_file:
            log_file.write(next_cursor + "\n")
        print(f"[INFO] Checked cursor logged to {checked_cursors_log}")

if __name__ == "__main__":
    main()