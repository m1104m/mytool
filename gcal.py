import sys
from datetime import datetime, timedelta
from googleapiclient.discovery import build
from google.oauth2 import service_account
import calendar

# ===== 設定 =====
SERVICE_ACCOUNT_FILE = 'credentials.json'
SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']
CALENDAR_ID = '1bf61072219748b7c620a70df9f5495d76f90694cef59a129449b2c4eff599b7@group.calendar.google.com'
# ===============

def get_month_range(year: int, month: int):
    """指定年月の開始と終了のdatetimeを返す"""
    start = datetime(year, month, 1, 0, 0, 0)
    last_day = calendar.monthrange(year, month)[1]
    end = datetime(year, month, last_day, 23, 59, 59)
    return start, end

def main():
    # 引数処理
    args = sys.argv[1:]
    now = datetime.now()

    if not args:
        # デフォルトは今月
        target_year = now.year
        target_month = now.month
    elif args[0] == "prev":
        # 「prev」指定で前月
        prev_month_last_day = now.replace(day=1) - timedelta(days=1)
        target_year = prev_month_last_day.year
        target_month = prev_month_last_day.month
    else:
        # YYYY MM 形式で指定
        try:
            target_year = int(args[0])
            target_month = int(args[1])
        except (ValueError, IndexError):
            print("使い方: python count_events.py [prev] または [YYYY MM]")
            sys.exit(1)

    start_dt, end_dt = get_month_range(target_year, target_month)

    # Google API認証
    creds = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=SCOPES
    )
    service = build('calendar', 'v3', credentials=creds)

    # イベント取得
    events_result = service.events().list(
        calendarId=CALENDAR_ID,
        timeMin=start_dt.isoformat() + 'Z',
        timeMax=end_dt.isoformat() + 'Z',
        singleEvents=True
    ).execute()
    events = events_result.get('items', [])

    # カウント出力
    print(f"{target_year}年{target_month}月の件数: {len(events)}")

if __name__ == "__main__":
    main()

