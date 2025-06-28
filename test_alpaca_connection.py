import os
import requests
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("ALPACA_API_KEY")
SECRET_KEY = os.getenv("ALPACA_SECRET_KEY")
BASE_URL = os.getenv("ALPACA_BASE_URL", "https://paper-api.alpaca.markets")

HEADERS = {
    "APCA-API-KEY-ID": API_KEY,
    "APCA-API-SECRET-KEY": SECRET_KEY,
}

def check_connection():
    r = requests.get(f"{BASE_URL}/v2/account", headers=HEADERS)
    if r.status_code == 200:
        print("✅ Alpaca APIに接続成功")
        print(r.json())
    else:
        print(f"❌ 接続失敗: {r.status_code}")
        print(r.text)

if __name__ == "__main__":
    check_connection()
