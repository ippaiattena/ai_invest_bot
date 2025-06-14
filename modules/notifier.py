import os
import requests
from datetime import datetime
import gspread
from gspread_dataframe import set_with_dataframe

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

    save_to_csv(df)    # 不要なら消して良い
    save_to_sheet(df)

def save_to_csv(df):
    if df.empty:
        return
    os.makedirs("data", exist_ok=True)
    today_str = datetime.today().strftime("%Y-%m-%d")
    filename = f"data/screening_log_{today_str}.csv"
    df.to_csv(filename, index=False)
    print(f"CSV保存完了: {filename}")

def save_to_sheet(df):
    if df.empty:
        return

    # 認証
    gc = gspread.service_account(filename='credentials.json')

    # スプレッドシートのID or URL（例：シートURLの /d/XXX の部分）
    SPREADSHEET_ID = '1gFROcwTXReZVnM3XWKNoRDsiejfkSNtwoQbB8SMsePs'
    sheet = gc.open_by_key(SPREADSHEET_ID).worksheet("daily")

    # 日付列を追加
    df['Date'] = datetime.today().strftime("%Y-%m-%d")

    # 既存行数を取得（ヘッダー＋既存データ）
    existing_rows = len(sheet.get_all_values())

    # 書き込み（1行目はヘッダーなので +1 して新しい行に追加）
    set_with_dataframe(sheet, df, row=existing_rows+1, include_column_header=existing_rows == 0)