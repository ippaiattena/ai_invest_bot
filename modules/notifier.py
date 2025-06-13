import os
import requests
from datetime import datetime

WEBHOOK_URL = os.environ.get("SLACK_WEBHOOK_URL")

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

    save_to_csv(df)

def save_to_csv(df):
    if df.empty:
        return
    os.makedirs("data", exist_ok=True)
    today_str = datetime.today().strftime("%Y-%m-%d")
    filename = f"data/screening_log_{today_str}.csv"
    df.to_csv(filename, index=False)
    print(f"CSV保存完了: {filename}")
