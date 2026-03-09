import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime, timedelta

SCOPES = ["https://www.googleapis.com/auth/spreadsheets.readonly"]
creds = Credentials.from_service_account_file("credentials.json", scopes=SCOPES)
gc = gspread.authorize(creds)

SPREADSHEET_ID = "1P5H00BD_2QPzdKAqgoCHm7FMKlnAp1NzvRey8NCVvaU"
sh = gc.open_by_key(SPREADSHEET_ID)

tomorrow = datetime.now().date() + timedelta(days=1)
tomorrow_str = tomorrow.strftime("%Y/%m/%d")  # シートが yyyy/mm/dd なのでここを合わせる[web:32]

def get_menu(sheet_name):
    ws = sh.worksheet(sheet_name)
    rows = ws.get_all_values()
    header = rows[0]
    data_rows = rows[1:]

    date_col = 0  # A列
    menu_col = 2  # C列

    menus = []
    for row in data_rows:
        if len(row) <= menu_col:
            continue
        if row[date_col] == tomorrow_str:
            menu_raw = row[menu_col]
            # 全角スペース(\u3000)を削除 or 半角スペースに[web:81][web:84]
            menu = menu_raw.replace("\u3000", "・")  # 消す
            menus.append(menu)

    return menus

satsuki_menus = get_menu("咲月")
koki_menus = get_menu("孝紀")

print("【咲月の献立】\n", satsuki_menus)
print("\n\n【孝紀の献立】\n", koki_menus)

