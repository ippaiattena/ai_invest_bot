# .env ファイルについて（ローカル実行用）

ローカル実行で Slack 通知や Google Sheets 保存を行うには `.env` を使って環境変数を読み込ませます。

## 書き方例

```
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/XXX/YYY/ZZZ
SLACK_BOT_TOKEN=xoxb-XXXXXXXXXXXXXXXXXXXXXX
```

markdown
コピーする
編集する

## 注意点

- `.env` ファイルは `.gitignore` に含め、リポジトリにコミットしないようにしてください。
- GitHub Actions 上では `secrets` を用いるため `.env` は不要です。

## 使用方法

- `dotenv` を使って `.env` を読み込むには `python-dotenv` が必要です。

```bash
pip install python-dotenv
```

- main.py 内で自動読み込みされます。

```python
from dotenv import load_dotenv
load_dotenv()
```
