import sys
import yaml
from modules import screening, notifier
from modules.backtest_runner import run_backtest_multiple
from slack_notifier import send_slack_message
from exit_rules import EXIT_RULES
from modules.broker_factory import create_broker

RESET_WALLET = "--reset" in sys.argv

# ① 複数銘柄バックテスト実行
with open("config.yaml", "r", encoding="utf-8") as f:
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

# 発注モード取得
order_mode = config.get("order").get("mode", "dummy")
exit_rule_name = config.get("order", {}).get("exit_rule", "rsi")
exit_rule_func = EXIT_RULES.get(exit_rule_name)
exit_rule_config = {
    "rsi_threshold": rsi_threshold,
}

# Broker 初期化（共通）
broker = create_broker(order_mode, reset_wallet=RESET_WALLET)
    
# 自動売買シグナル処理
broker.process_signals(results)
if order_mode == "local":
    if exit_rule_func is not None:
        rule = lambda df: exit_rule_func(df, exit_rule_config)
    else:
        rule = None
    broker.apply_exit_strategy(results, rule_func=rule)

# Slack通知（スクリーニング + トレードサマリー + GSS保存）
notifier.notify(results, backtest_results=backtest_results, local_broker=broker if order_mode == "local" else None)

# 保有資産サマリー出力（localモード時のみ）
if order_mode == "local":
    summary = broker.get_portfolio_summary()
    print("\n=== 💼 保有資産サマリー ===")
    print(broker.format_portfolio_summary())

# 動作確認用のSlack通知（なくてもOK）
send_slack_message("✅ Slack通知テスト：Botは正常に動いています。")
