import yaml
from modules import screening, notifier

with open("config.yaml", "r") as f:
    config = yaml.safe_load(f)

tickers = config["tickers"]
rsi_threshold = config.get("rsi_threshold", 70)

results = screening.run_screening(tickers, rsi_threshold)
notifier.notify(results)
