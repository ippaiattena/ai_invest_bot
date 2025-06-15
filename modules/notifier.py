import os
import requests
from datetime import datetime
import gspread
from gspread_dataframe import set_with_dataframe
import pandas as pd
import mimetypes
import slack_sdk
from slack_sdk.web import WebClient
from dotenv import load_dotenv
import dataframe_image as dfi
from modules.plotting import plot_metric_trend

# .envファイルの読み込み（ローカル環境用）
load_dotenv()

WEBHOOK_URL = os.getenv("SLACK_WEBHOOK_URL")
SLACK_BOT_TOKEN = os.getenv("SLACK_BOT_TOKEN")  # ← 追加
CLIENT = WebClient(token=SLACK_BOT_TOKEN)       # ← 追加

def notify(df, backtest_results=None):

    message = build_slack_message(df, backtest_results)

    payload = {"text": message}
    response = requests.post(WEBHOOK_URL, json=payload)

    if response.status_code != 200:
        print(f"Slack通知失敗: {response.status_code} - {response.text}")
    else:
        print("Slackに通知しました。")

    save_to_csv(df)    # 不要なら消して良い
    save_to_sheet(df)
    
    # バックテスト結果があれば GSS 保存
    if backtest_results:
        save_backtest_metrics_to_sheet(backtest_results)

    # 評価指標をCSV保存＆Slack送信
    csv_path = save_backtest_metrics_csv(backtest_results)
    if csv_path:
        send_metrics_csv_as_image(csv_path)
        # 指標CSVを全期間ログに追記
        metrics_df = pd.read_csv(csv_path)
        append_to_all_metrics_log(metrics_df)

    # チャート画像があればSlackに送信
    chart_path = f"data/backtest_plot_mpl_AAPL.png"
    if os.path.exists(chart_path):
        send_chart_to_slack(chart_path)

    # チャート画像を時系列で生成・通知
    try:
        all_path = "data/backtest_metrics_all.csv"
        if os.path.exists(all_path):
            all_df = pd.read_csv(all_path)
            for metric in ["CAGR", "Sharpe", "Max Drawdown"]:
                chart_path = f"data/trend_{metric.replace(' ', '_')}.png"
                plot_metric_trend(all_df, metric, chart_path)
                send_chart_to_slack(chart_path)
    except Exception as e:
        print(f"📉 指標推移グラフ生成失敗: {e}")

def build_slack_message(df, backtest_results):
    lines = [":robot_face: *AI投資Bot通知*"]

    # --- シグナル ---
    if df.empty:
        lines.append("📉 *本日Buyシグナルはありません*")
    else:
        buy_df = df[df["Signal"] == "Buy"]
        others_df = df[df["Signal"] != "Buy"]

        if not buy_df.empty:
            lines.append("\n📈 *本日のBuy候補*")
            for _, row in buy_df.iterrows():
                lines.append(f"- `{row['Ticker']}`: *Buy* @ {row['Close']} (RSI: {row['RSI']})")

        if not others_df.empty:
            lines.append("\n📊 *その他のシグナル*")
            for _, row in others_df.iterrows():
                lines.append(f"- `{row['Ticker']}`: {row['Signal']} @ {row['Close']} (RSI: {row['RSI']})")

    # --- バックテスト要約 ---
    if backtest_results:
        lines.append("\n📋 *バックテスト評価サマリー*")
        for r in backtest_results:
            m = r.get("metrics", {})
            if m:
                lines.append(
                    f"- {r['ticker']}: 勝率 {m.get('win_rate', 0):.1f}%, "
                    f"CAGR {m.get('cagr', 0):.2%}, "
                    f"最大DD {m.get('max_drawdown', 0):.2f}%"
                )

    lines.append("\n🔗 *詳細CSV・チャートは添付ファイルを参照*")
    return "\n".join(lines)

def save_to_csv(df):
    if df.empty:
        return
    os.makedirs("data", exist_ok=True)
    today_str = datetime.today().strftime("%Y-%m-%d")
    filename = f"data/screening_log_{today_str}.csv"
    df.to_csv(filename, index=False)
    print(f"CSV保存完了: {filename}")

def save_backtest_metrics_csv(results):
    if not results:
        return

    today = datetime.today().strftime("%Y-%m-%d")
    rows = []
    for r in results:
        m = r["metrics"]
        rows.append({
            "Date": today,
            "Ticker": r["ticker"],
            "Total Return": m.get("total_return"),
            "CAGR": m.get("cagr"),
            "Sharpe": m.get("sharpe"),
            "Max Drawdown": m.get("max_drawdown"),
            "Avg Profit": m.get("avg_profit"),
            "Win Rate": m.get("win_rate"),
            "Avg Hold Days": m.get("avg_hold_days"),
        })
    df = pd.DataFrame(rows)
    os.makedirs("data", exist_ok=True)
    csv_path = f"data/backtest_metrics_{today}.csv"
    df.to_csv(csv_path, index=False)
    print(f"📄 指標CSVを保存しました: {csv_path}")
    return csv_path

def send_metrics_csv_as_image(csv_path):
    try:
        df = pd.read_csv(csv_path)
        img_path = csv_path.replace(".csv", ".png")
        dfi.export(df, img_path, table_conversion="matplotlib")
        send_chart_to_slack(img_path)
    except Exception as e:
        print(f"📤 CSV画像化または送信失敗: {e}")

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

def save_backtest_metrics_to_sheet(results):
    if not results:
        return

    # Google Sheets 認証
    gc = gspread.service_account(filename='credentials.json')
    SPREADSHEET_ID = '1gFROcwTXReZVnM3XWKNoRDsiejfkSNtwoQbB8SMsePs'
    try:
        sheet = gc.open_by_key(SPREADSHEET_ID).worksheet("backtest_metrics")
    except gspread.exceptions.WorksheetNotFound:
        # なければ作成（末尾に追加）
        spreadsheet = gc.open_by_key(SPREADSHEET_ID)
        sheet = spreadsheet.add_worksheet(title="backtest_metrics", rows="1000", cols="20")

    today = datetime.today().strftime("%Y-%m-%d")
    rows = []

    for result in results:
        m = result.get("metrics", {})
        rows.append({
            "Date": today,
            "Ticker": result["ticker"],
            "Total Return": m.get("total_return"),
            "CAGR": m.get("cagr"),
            "Sharpe": m.get("sharpe"),
            "Max Drawdown": m.get("max_drawdown"),
            "Avg Profit": m.get("avg_profit"),
            "Win Rate": m.get("win_rate"),
            "Avg Hold Days": m.get("avg_hold_days"),
        })

    df = pd.DataFrame(rows)
    existing_rows = len(sheet.get_all_values())
    set_with_dataframe(sheet, df, row=existing_rows+1, include_column_header=existing_rows == 0)

def send_chart_to_slack(filepath):
    try:
        title = "📊 バックテストチャート" if "plot" in filepath else "📋 指標サマリー"

        with open(filepath, "rb") as f:
            result = CLIENT.files_upload_v2(
                file=f,
                filename=os.path.basename(filepath),
                title="📊 バックテストチャート",
                channels=["C0918E8KW6P"]  # チャンネル名（#なし、リストで）
            )
        if result["ok"]:
            print(f"{title}（{os.path.basename(filepath)}）をSlackに送信しました。")
        else:
            print(f"Slackファイル送信失敗: {result['error']}")
    except Exception as e:
        print(f"チャート画像の送信中にエラー発生: {e}")

def append_to_all_metrics_log(df):
    """日付×銘柄で重複排除して backtest_metrics_all.csv に追記"""
    if df is None or df.empty:
        return
    path = "data/backtest_metrics_all.csv"
    if os.path.exists(path):
        existing = pd.read_csv(path)
        df = pd.concat([existing, df]).drop_duplicates(subset=["Date", "Ticker"], keep="last")
    df.to_csv(path, index=False)
    print(f"🗂️ 全期間ログ更新: {path}")
