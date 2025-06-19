import os
import requests

# あなたのSlackトークンと通知先チャンネルをここに
SLACK_BOT_TOKEN = os.getenv("SLACK_BOT_TOKEN")
CHANNEL_ID = os.getenv("SLACK_CHANNEL")

def send_slack_message(message):
    url = "https://slack.com/api/chat.postMessage"
    headers = {"Authorization": f"Bearer {SLACK_BOT_TOKEN}"}
    data = {
        "channel": CHANNEL_ID,
        "text": message
    }

    response = requests.post(url, headers=headers, data=data)

    if not response.ok or not response.json().get("ok"):
        print("Slack通知に失敗しました:", response.text)
    else:
        print("Slackに通知しました。")
