from google_auth_oauthlib.flow import InstalledAppFlow

SCOPES = ["https://www.googleapis.com/auth/calendar.readonly"]
CREDENTIALS_PATH = "credentials.json"
TOKEN_PATH = "token.json"

def main():
    flow = InstalledAppFlow.from_client_secrets_file(
        CREDENTIALS_PATH,
        SCOPES,
    )
    # open_browser=False にして、URL を必ず表示させる
    creds = flow.run_local_server(
        port=0,
        authorization_prompt_message="このURLをブラウザで開いてください:\n{url}\n",
        success_message="認可が完了しました。このウィンドウを閉じてOKです。",
        open_browser=False,
    )
    with open(TOKEN_PATH, "w") as f:
        f.write(creds.to_json())
    print("token.json を保存しました")

if __name__ == "__main__":
    main()

