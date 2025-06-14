import yaml
import subprocess
from modules import screening, notifier
from slack_notifier import send_slack_message

# ① バックテスト実行
subprocess.run(["python", "backtest.py"])

# スクリーニング処理
with open("config.yaml", "r") as f:
    config = yaml.safe_load(f)

tickers = config["tickers"]
rsi_threshold = config.get("rsi_threshold", 70)

results = screening.run_screening(tickers, rsi_threshold)

# Slack通知（スクリーニング + トレードサマリー）
notifier.notify(results)

# 動作確認用のSlack通知（なくてもOK）
send_slack_message("✅ Slack通知テスト：Botは正常に動いています。")