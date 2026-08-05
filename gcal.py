import csv
import sys
from datetime import date, datetime, timedelta
from zoneinfo import ZoneInfo
from googleapiclient.discovery import build
from google.oauth2 import service_account

# ===== 設定 =====
SERVICE_ACCOUNT_FILE = 'credentials.json'
SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']
CALENDAR_ID = '1bf61072219748b7c620a70df9f5495d76f90694cef59a129449b2c4eff599b7@group.calendar.google.com'
JST = ZoneInfo('Asia/Tokyo')
# ===============

def get_month_range(year: int, month: int):
    """指定年月の開始と終了(翌月初日=終端は排他)のdatetimeをJSTで返す"""
    start = datetime(year, month, 1, tzinfo=JST)
    if month == 12:
        end = datetime(year + 1, 1, 1, tzinfo=JST)
    else:
        end = datetime(year, month + 1, 1, tzinfo=JST)
    return start, end

def get_year_range(year: int):
    """指定年の開始と終了(翌年初日=終端は排他)のdatetimeをJSTで返す"""
    start = datetime(year, 1, 1, tzinfo=JST)
    end = datetime(year + 1, 1, 1, tzinfo=JST)
    return start, end

def count_events(service, start_dt: datetime, end_dt: datetime) -> int:
    """指定期間のイベント件数を返す(ページネーション対応)"""
    count = 0
    page_token = None
    while True:
        events_result = service.events().list(
            calendarId=CALENDAR_ID,
            timeMin=start_dt.isoformat(),
            timeMax=end_dt.isoformat(),
            singleEvents=True,
            maxResults=2500,
            pageToken=page_token,
        ).execute()
        count += len(events_result.get('items', []))
        page_token = events_result.get('nextPageToken')
        if not page_token:
            return count

def fetch_events(service, start_dt: datetime, end_dt: datetime) -> list[dict]:
    """指定期間のイベントを開始日時順に全件返す(ページネーション対応)"""
    events = []
    page_token = None
    while True:
        events_result = service.events().list(
            calendarId=CALENDAR_ID,
            timeMin=start_dt.isoformat(),
            timeMax=end_dt.isoformat(),
            singleEvents=True,
            orderBy='startTime',
            maxResults=2500,
            pageToken=page_token,
        ).execute()
        events.extend(events_result.get('items', []))
        page_token = events_result.get('nextPageToken')
        if not page_token:
            return events

def event_start_date(event: dict) -> date:
    """イベントの開始日をJSTの日付として返す"""
    start = event.get('start', {})
    if 'dateTime' in start:
        # 終日以外: タイムゾーン付きの日時。JSTに揃えてから日付を取る
        return datetime.fromisoformat(start['dateTime']).astimezone(JST).date()
    # 終日イベント: YYYY-MM-DD
    return date.fromisoformat(start['date'])

def export_csv(service, start_dt: datetime, end_dt: datetime, out_path: str) -> int:
    """指定期間のイベントを「項目名,YYYY/MM/DD」形式でCSV出力し、件数を返す"""
    events = fetch_events(service, start_dt, end_dt)
    with open(out_path, 'w', newline='', encoding='utf-8-sig') as f:
        writer = csv.writer(f)
        for event in events:
            summary = event.get('summary', '(タイトルなし)')
            writer.writerow([summary, event_start_date(event).strftime('%Y/%m/%d')])
    return len(events)

def run_csv_mode(args: list[str], now: datetime):
    """csvサブコマンド: 1年分のイベントをCSV出力する"""
    if not args:
        # 年指定なし: 今年
        target_year = now.year
    elif len(args[0]) == 4 and args[0].isdigit():
        target_year = int(args[0])
    else:
        print("使い方: python gcal.py csv [YYYY] [出力先.csv]")
        sys.exit(1)

    out_path = args[1] if len(args) > 1 else f"gcal_{target_year}.csv"
    start_dt, end_dt = get_year_range(target_year)

    service = build('calendar', 'v3', credentials=load_credentials())
    total = export_csv(service, start_dt, end_dt, out_path)
    print(f"{target_year}年の{total}件を {out_path} に出力しました。")

def load_credentials():
    """サービスアカウントの認証情報を返す"""
    return service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=SCOPES
    )

def main():
    args = sys.argv[1:]
    now = datetime.now(JST)

    if args and args[0] == "csv":
        run_csv_mode(args[1:], now)
        return

    # モードと対象期間を決定
    mode = "month"  # "month" or "year"

    if not args:
        # 引数なし: 今月
        target_year = now.year
        target_month = now.month
        start_dt, end_dt = get_month_range(target_year, target_month)

    elif args[0] == "prev":
        # 「prev」指定で前月
        prev_month_last_day = now.replace(day=1) - timedelta(days=1)
        target_year = prev_month_last_day.year
        target_month = prev_month_last_day.month
        start_dt, end_dt = get_month_range(target_year, target_month)

    else:
        arg = args[0]
        # 4桁: 年指定 (YYYY)
        if len(arg) == 4 and arg.isdigit():
            mode = "year"
            target_year = int(arg)
            start_dt, end_dt = get_year_range(target_year)
        # 6桁: 年月指定 (YYYYMM)
        elif len(arg) == 6 and arg.isdigit():
            mode = "month"
            target_year = int(arg[:4])
            target_month = int(arg[4:6])
            if not (1 <= target_month <= 12):
                print("月は01〜12で指定してください。")
                sys.exit(1)
            start_dt, end_dt = get_month_range(target_year, target_month)
        else:
            print("使い方: python gcal.py [prev] | [YYYY] | [YYYYMM] | csv [YYYY] [出力先.csv]")
            sys.exit(1)

    # Google API認証
    service = build('calendar', 'v3', credentials=load_credentials())

    # イベント取得
    total = count_events(service, start_dt, end_dt)

    # 結果出力
    if mode == "year":
        print(f"{target_year}年の件数: {total}")
    else:
        print(f"{target_year}年{target_month}月の件数: {total}")

if __name__ == "__main__":
    main()

