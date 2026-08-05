import sys
from datetime import datetime, timedelta
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

def main():
    args = sys.argv[1:]
    now = datetime.now(JST)

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
            print("使い方: python gcal.py [prev] | [YYYY] | [YYYYMM]")
            sys.exit(1)

    # Google API認証
    creds = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=SCOPES
    )
    service = build('calendar', 'v3', credentials=creds)

    # イベント取得
    total = count_events(service, start_dt, end_dt)

    # 結果出力
    if mode == "year":
        print(f"{target_year}年の件数: {total}")
    else:
        print(f"{target_year}年{target_month}月の件数: {total}")

if __name__ == "__main__":
    main()

