import yaml
from modules import screening, notifier
from modules.backtest_runner import run_backtest_multiple
from slack_notifier import send_slack_message

# ① 複数銘柄バックテスト実行
with open("config.yaml", "r") as f:
    config = yaml.safe_load(f)

tickers = config["tickers"]
rsi_threshold = config.get("rsi_threshold", 70)
start_date = config.get("backtest_start", "2023-01-01")
end_date = config.get("backtest_end", "2024-01-01")

backtest_results = run_backtest_multiple(tickers, start=start_date, end=end_date)

# バックテスト評価指標の要約をSlack通知用に整形
summary_lines = [":chart_with_upwards_trend: *バックテスト評価指標*"]
for result in backtest_results:
    metrics = result.get("metrics", {})
    if not metrics:
        continue
    line = (
        f"- {result['ticker']} | "
        f"総トレード: {metrics['total_trades']}, "
        f"勝率: {metrics['win_rate']:.1f}%, "
        f"CAGR: {metrics['cagr']:.2%}, "
        f"最大DD: {metrics['max_drawdown']:.2f}%"
    )
    summary_lines.append(line)

if len(summary_lines) > 1:
    send_slack_message("\n".join(summary_lines))

# スクリーニング処理
results = screening.run_screening(tickers, rsi_threshold)

# Slack通知（スクリーニング + トレードサマリー + GSS保存）
notifier.notify(results, backtest_results=backtest_results)

# 動作確認用のSlack通知（なくてもOK）
send_slack_message("✅ Slack通知テスト：Botは正常に動いています。")
