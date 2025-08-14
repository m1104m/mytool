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

# Todoist APIから完了タスク取得
headers = {
    "Authorization": f"Bearer {API_TOKEN}"
}
params = {
    "since": yesterday.replace(hour=0, minute=0, second=0).isoformat(),
    "until": yesterday.replace(hour=23, minute=59, second=59).isoformat()
}
response = requests.get(
    "https://api.todoist.com/sync/v9/completed/get_all",
    headers=headers,
    params=params
)

# API エラーハンドリング
if response.status_code != 200:
    print("❌ Todoist APIの呼び出しに失敗しました:", response.text)
    exit(1)

completed_items = response.json().get("items", [])

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

