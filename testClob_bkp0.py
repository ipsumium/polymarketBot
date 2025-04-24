import os
import json
from py_clob_client.client import ClobClient
from py_clob_client.constants import POLYGON
from dotenv import load_dotenv

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
    next_cursor = None  # Start with None, not "" or 0

    while True:
        print(f"[DEBUG] Fetching markets with next_cursor: {next_cursor!r}")
        try:
            # Only include next_cursor if it's not None
            if next_cursor is None:
                response = client.get_markets()
            else:
                response = client.get_markets(next_cursor=next_cursor)

            print(f"[DEBUG] Raw response keys: {list(response.keys())}")

            if 'data' in response:
                print(f"[DEBUG] Number of markets in this page: {len(response['data'])}")
                markets.extend(response['data'])
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

    print(f"\n✅ Successfully fetched {len(markets)} markets")
    if markets:
        print(f"[DEBUG] First market: {json.dumps(markets[0], indent=2)}")

if __name__ == "__main__":
    main()
