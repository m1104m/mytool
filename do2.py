import requests

API_TOKEN = "b74d73d95e79061586b64a1fc1e6eb27676139ac"
headers = {"Authorization": f"Bearer {API_TOKEN}"}

urls = [
    "https://api.todoist.com/api/v1/tasks/completed",
    "https://api.todoist.com/api/v1/tasks?is_completed=true",
    "https://api.todoist.com/api/v1/tasks?filter=completed",
    "https://api.todoist.com/api/v1/activity",
    "https://api.todoist.com/api/v1/activity/get",
]

for url in urls:
    r = requests.get(url, headers=headers)
    print(f"{url} → {r.status_code}: {r.text[:100]}")
