import os
import requests
from datetime import datetime
import gspread
from gspread_dataframe import set_with_dataframe
import pandas as pd
import mimetypes
import slack_sdk
from slack_sdk.web import WebClient

WEBHOOK_URL = os.getenv("SLACK_WEBHOOK_URL")
SLACK_BOT_TOKEN = os.getenv("SLACK_BOT_TOKEN")  # ← 追加
CLIENT = WebClient(token=SLACK_BOT_TOKEN)       # ← 追加

def notify(df):
    if df.empty:
        message = "📉 No Buy signals today."
    else:
        message = "*📈 AI Screening Results*\n"
        for _, row in df.iterrows():
            line = f"- `{row['Ticker']}`: *{row['Signal']}* @ {row['Close']} (RSI: {row['RSI']})"
            message += line + "\n"

    # --- 売買ログが存在すればトレードサマリーを追記 ---
    trade_log_path = "data/backtest_trades_AAPL_2023-01-01_to_2024-01-01.csv"
    if os.path.exists(trade_log_path):
        trade_df = pd.read_csv(trade_log_path)
        sell_df = trade_df[trade_df['type'] == 'SELL'].dropna()
        if not sell_df.empty:
            total = len(sell_df)
            wins = (sell_df['profit'] > 0).sum()
            avg_profit = sell_df['profit'].mean()
            avg_holding = sell_df['holding_days'].mean()
            summary = (
                "\n:chart_with_upwards_trend: *トレードサマリー*\n"
                f"- 総トレード数       : {total}\n"
                f"- 勝率               : {wins / total * 100:.1f}%\n"
                f"- 平均損益           : {avg_profit:.2f}\n"
                f"- 平均保有期間（日） : {avg_holding:.1f}日"
            )
            message += summary

    payload = {"text": message}
    response = requests.post(WEBHOOK_URL, json=payload)

    if response.status_code != 200:
        print(f"Slack通知失敗: {response.status_code} - {response.text}")
    else:
        print("Slackに通知しました。")

    save_to_csv(df)    # 不要なら消して良い
    save_to_sheet(df)

    # チャート画像があればSlackに送信
    chart_path = f"data/backtest_plot_mpl_AAPL.png"
    if os.path.exists(chart_path):
        send_chart_to_slack(chart_path)

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

def send_chart_to_slack(filepath):
    try:
        response = CLIENT.files_upload(
            channels="#general",  # ← チャンネル名やIDに変更可能
            file=filepath,
            title="📊 バックテストチャート",
            filename=os.path.basename(filepath),
            filetype=mimetypes.guess_type(filepath)[0] or "image/png"
        )
        if not response["ok"]:
            print(f"Slackファイル送信失敗: {response['error']}")
        else:
            print("チャート画像をSlackに送信しました。")
    except Exception as e:
        print(f"チャート画像の送信中にエラー発生: {e}")
