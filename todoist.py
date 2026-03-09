import os
import urllib.parse
import requests

API_TOKEN = "b74d73d95e79061586b64a1fc1e6eb27676139ac" 

def fetch_today_tasks():
    base_url = "https://api.todoist.com/rest/v2/tasks"
    headers = {"Authorization": f"Bearer {API_TOKEN}"}

    # フィルタ文字列を URL エンコード（today, today & @work など）[web:9][web:80]
    filter_raw = "today"
    params = {"filter": filter_raw}

    resp = requests.get(base_url, headers=headers, params=params)
    resp.raise_for_status()
    return resp.json()  # list[dict]

def print_today_tasks():
    tasks = fetch_today_tasks()

    if not tasks:
        print("今日のタスクはありません")
        return

    for t in tasks:
        content = t["content"]
        due = t.get("due") or {}
        date = due.get("date")  # "YYYY-MM-DD" 形式[web:9]
        print(f"□ {content}")

if __name__ == "__main__":
    print_today_tasks()

