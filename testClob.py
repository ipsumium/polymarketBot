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
    next_cursor = ""   # Start with  ""
    timestamp_format = "%Y-%m-%d %H:%M:%S"
    cursor_history = []

    while len(markets) < 100:
        print(f"[DEBUG] Fetching markets with next_cursor: {next_cursor}")
        try:
            response = client.get_markets(next_cursor=next_cursor)
            
            if 'data' in response:
                filtered_markets = [market for market in response['data'] if not market.get("closed", True) and market.get("active", False)]
                markets.extend(filtered_markets)
            else:
                print("[DEBUG] No 'data' key in response, full response:", json.dumps(response, indent=2))
                break
            
            next_cursor = response.get("next_cursor")
            cursor_history.append(next_cursor)
        
            if not next_cursor or next_cursor == "LTE=":
                print("[DEBUG] No more pages to fetch or end cursor received.")
                break
        except Exception as e:
            print(f"[ERROR] Exception during API call: {e}")
            break
    
    timestamp = datetime.now().strftime(timestamp_format)
    # markets_with_timestamp = {"timestamp": timestamp, "markets": markets[:100]}
    output_file = f"open_markets_{timestamp}.json"
    with open(output_file, 'w') as f:
        json.dump(markets, f, indent=4)
        print(f"[INFO] Markets have been saved to {output_file}")
    output_file = f"checked_cursors_{timestamp}.json"
    with open(output_file, 'w') as f:
        json.dump(cursor_history, f, indent=4)
        print(f"[INFO] Cursor history has been saved to {output_file}")
    print(f"[INFO] Total markets fetched: {len(markets)}")
    print(f"[INFO] Cursor history length: {len(cursor_history)}")

if __name__ == "__main__":
    main()