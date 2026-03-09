import sys
try:
    import gpsoauth
except ImportError:
    print("gpsoauthがインストールされていません。インストール中...")
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "gpsoauth"])
    import gpsoauth

# パラメータ（以下を実際の値に置き換えてください）
email = "m1104m@gmail.com"  # Google Keepを使用しているGoogleアカウントのメールアドレス
oauth_token = "oauth2_4/0Ab32j93BaXMvEOnhtGSsoNx8Ma74fmttSuNMeYDCVpaHVT0Tk0bDDJFt5gSSCzsL161MzQ"  # 手順2-1で取得するOAuthトークン(後述)
android_id = "355314360755520"    # 手順2-2で取得するAndroid ID(後述)

try:
    result = gpsoauth.exchange_token(email, oauth_token, android_id)
    print("結果:", result)  # 出力されるJSONレスポンスの「Token」の値がGOOGLE_MASTER_TOKENです
except Exception as e:
    print("エラー:", e) 

