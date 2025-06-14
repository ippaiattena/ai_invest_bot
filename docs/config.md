# config.yaml 設定ファイル仕様

`main.py` などの各種スクリプトは、`config.yaml` を読み込み動作を制御します。

## 構造

```yaml
tickers:
  - AAPL
  - MSFT
  - GOOG
  - AMZN
  - META

rsi_threshold: 70
```

| パラメータ           | 型    | 説明                    |
| --------------- | ---- | --------------------- |
| `tickers`       | list | 対象とする株式ティッカー一覧        |
| `rsi_threshold` | int  | RSIでのBuy判定閾値（デフォルト70） |

---

## 備考

- 今後 SMA 期間なども追加予定。
- .env ファイルや Secrets とは分離して運用します。
