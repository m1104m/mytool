import os
from datetime import datetime, timedelta
import requests

# === 設定 ===========================================
API_TOKEN = "b74d73d95e79061586b64a1fc1e6eb27676139ac"  # ★← ここに自身のトークンを入力
DIRECTORY = "/Users/murakihitoshi/Documents/Cloud/Daily Report"
# ====================================================

# 昨日の日付取得
yesterday = datetime.now() - timedelta(days=1)
date_str = yesterday.strftime('%Y-%m-%d')

# ファイルパス構築
filename = f"{date_str}.md"
filepath = os.path.join(DIRECTORY, filename)

# Todoist API v1 から完了タスク取得
headers = {
    "Authorization": f"Bearer {API_TOKEN}"
}
params = {
    "since": f"{date_str}T00:00:00",
    "until": f"{date_str}T23:59:59"
}

response = requests.get(
    "https://api.todoist.com/api/v1/tasks/completed",
    headers={"Authorization": f"Bearer {API_TOKEN}"},
    params={
        "since": f"{date_str}T00:00:00",
        "until": f"{date_str}T23:59:59"
    }
)

# API エラーハンドリング
if response.status_code != 200:
    print("❌ Todoist APIの呼び出しに失敗しました:", response.text)
    exit(1)

data = response.json()

# 新API v1ではレスポンスが {"items": [...]} またはリスト直接の場合がある
if isinstance(data, list):
    completed_items = data
elif isinstance(data, dict):
    completed_items = data.get("items", data.get("results", []))
else:
    completed_items = []

# 追記するテキスト構成
lines = ["\n# Todoistでの完了項目\n"]
if completed_items:
    for item in completed_items:
        lines.append(f"- {item.get('content', '（内容なし）')}")
else:
    lines.append("- 完了タスクはありません。")

append_text = "\n".join(lines) + "\n"

# ディレクトリがなければ作成
if not os.path.exists(DIRECTORY):
    os.makedirs(DIRECTORY)

# ファイルが存在しない場合は新規作成（初期コンテンツ含む）
if not os.path.exists(filepath):
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(append_text)
    print(f"✅ ファイルが存在しなかったため新規作成しました: {filepath}")
else:
    # ファイルがある場合は末尾に追記
    with open(filepath, "a", encoding="utf-8") as f:
        f.write(append_text)
    print(f"✅ 既存ファイルの末尾に追記しました: {filepath}")
