import os
import requests
from dotenv import load_dotenv

load_dotenv()
WEBHOOK_URL = os.getenv("SLACK_WEBHOOK_URL")

def notify(df):
    if df.empty:
        message = "📉 No Buy signals today."
    else:
        message = "*📈 AI Screening Results*\n"
        for _, row in df.iterrows():
            line = f"- `{row['Ticker']}`: *{row['Signal']}* @ {row['Close']} (RSI: {row['RSI']})"
            message += line + "\n"

    payload = {"text": message}
    response = requests.post(WEBHOOK_URL, json=payload)

    if response.status_code != 200:
        print(f"Slack通知失敗: {response.status_code} - {response.text}")
    else:
        print("Slackに通知しました。")
