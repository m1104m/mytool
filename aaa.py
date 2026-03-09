import datetime
import os

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# 読み取り専用スコープ
SCOPES = ["https://www.googleapis.com/auth/calendar.readonly"]


def get_credentials():
    """
    Google Calendar API の認証情報を取得
    - 初回はブラウザでOAuth認証
    - 2回目以降は token.json から再利用
    """
    creds = None
    token_path = "token.json"

    if os.path.exists(token_path):
        creds = Credentials.from_authorized_user_file(token_path, SCOPES)

    # 認証情報が無い or 無効ならログイン
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                "credentials.json", SCOPES
            )
            creds = flow.run_local_server(port=0)

        # 次回以降のために保存
        with open(token_path, "w") as token:
            token.write(creds.to_json())

    return creds


def list_calendars(service):
    """
    自分が閲覧可能なカレンダー一覧を表示
    共有カレンダーもここに出てくるので、summary と id をメモしておく
    """
    calendar_list = service.calendarList().list().execute()
    print("=== カレンダー一覧 ===")
    for cal in calendar_list.get("items", []):
        print(f"summary: {cal.get('summary')}, id: {cal.get('id')}")
    print("======================")


def get_events(service, calendar_id, max_results=10):
    """
    指定カレンダーの今以降のイベントを取得して表示
    """
    try:
        now = datetime.datetime.now(tz=datetime.timezone.utc).isoformat()
        events_result = (
            service.events()
            .list(
                calendarId=calendar_id,
                timeMin=now,
                maxResults=max_results,
                singleEvents=True,
                orderBy="startTime",
            )
            .execute()
        )
        events = events_result.get("items", [])

        if not events:
            print("イベントが見つかりませんでした。")
            return

        print(f"=== カレンダーID: {calendar_id} のイベント ===")
        for event in events:
            summary = event.get("summary", "（タイトル未設定）")
            description = event.get("description", "（説明未設定）")
            start = event["start"].get("dateTime", event["start"].get("date"))
            end = event["end"].get("dateTime", event["end"].get("date"))
            location = event.get("location", "（場所未設定）")

            print(f"タイトル : {summary}")
            print(f"説明     : {description}")
            print(f"開始     : {start}")
            print(f"終了     : {end}")
            print(f"場所     : {location}")
            print("-----")

    except HttpError as error:
        print(f"API エラー: {error}")


def main():
    # 認証
    creds = get_credentials()
    service = build("calendar", "v3", credentials=creds)

    # まずは自分が見えるカレンダー一覧を出す（共有カレンダー含む）
    list_calendars(service)

    # ここに、取得したい共有カレンダーIDを貼る
    # 例: "xxxxxxx@group.calendar.google.com"
    calendar_id = input("取得したいカレンダーIDを入力してください: ").strip()

    # 予定取得
    get_events(service, calendar_id, max_results=10)


if __name__ == "__main__":
    main()

