import os
from py_clob_client.client import ClobClient
from py_clob_client.constants import POLYGON
from py_clob_client.clob_types import TradeParams
from dotenv import load_dotenv

load_dotenv()
private_key = os.getenv("POLYMARKET_PRIVATE_KEY")

def get_market_trades(condition_id: str) -> list:

    client = ClobClient(
        host="https://clob.polymarket.com",
        key=private_key,
        chain_id=POLYGON
    )
    api_creds = client.create_or_derive_api_creds()
    client.set_api_creds(api_creds)

    trades = []
    next_cursor = ""
    
    while True:
        response = client.get_trades(
            TradeParams={"market": condition_id, "next_cursor": next_cursor}
        )
        trades.extend(response.get("trades", []))
        next_cursor = response.get("next_cursor")
        if not next_cursor:
            break
    
    return trades

def calculate_volume(trades: list) -> float:
    return sum(float(trade["size"]) for trade in trades)

question_id = "0x6e3a19f10471e0b0f5c31119fae13603580557f926fca7dcc949767e538ce902"

condition_id="0x0346db74f1c1c7e8a05ef281df7992dccbb2df8a6a3b614d932ee93510a8600d"

# Fetch all trades
trades = get_market_trades(condition_id)

# Calculate and print volume
volume = calculate_volume(trades)
print(f"Total Volume: {volume:.2f} shares")
