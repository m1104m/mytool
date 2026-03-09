import os
import base64
import hashlib
import requests
from datetime import datetime, timezone
from email.utils import format_datetime
from xml.etree import ElementTree as ET

HATENA_ID = os.environ["HATENA_ID"]
HATENA_API_KEY = os.environ["HATENA_API_KEY"]
HATENA_BLOG_ID = os.environ["HATENA_BLOG_ID"]

# =========================
# フォトライフ: WSSEヘッダ生成
# =========================
def build_wsse(username: str, api_key: str) -> str:
    created = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    nonce = os.urandom(16)
    digest = hashlib.sha1(nonce + created.encode("utf-8") + api_key.encode("utf-8")).digest()
    b64nonce = base64.b64encode(nonce).decode("ascii")
    b64digest = base64.b64encode(digest).decode("ascii")
    return (
        f'UsernameToken Username="{username}", '
        f'PasswordDigest="{b64digest}", '
        f'Nonce="{b64nonce}", '
        f'Created="{created}"'
    )

# =========================
# フォトライフ: 画像アップロード
# =========================
def upload_to_fotolife(image_path: str, title: str) -> str:
    """
    画像をフォトライフにアップロードして、
    はてな記法の画像タグ（[f:id:...]）を返す。
    """
    with open(image_path, "rb") as f:
        data_b64 = base64.b64encode(f.read()).decode("ascii")

    entry_xml = f"""\
<entry xmlns="http://purl.org/atom/ns#">
  <title>{title}</title>
  <content mode="base64" type="image/png">
{data_b64}
  </content>
  <generator>python-script</generator>
</entry>
"""

    headers = {
        "X-WSSE": build_wsse(HATENA_ID, HATENA_API_KEY),
        "Content-Type": "application/xml",
        "Authorization": 'WSSE profile="UsernameToken"',
    }

    # フォトライフ AtomAPI PostURI[web:29]
    url = "https://f.hatena.ne.jp/atom/post"
    resp = requests.post(url, data=entry_xml.encode("utf-8"), headers=headers)
    resp.raise_for_status()

    # 返ってきたXMLから <hatena:syntax> を取得（[f:id:...]）[web:25][web:29]
    ns = {
        "atom": "http://purl.org/atom/ns#",
        "hatena": "http://www.hatena.ne.jp/info/xmlns#",
    }
    root = ET.fromstring(resp.content)
    syntax = root.find("hatena:syntax", ns)
    if syntax is None or not syntax.text:
        raise RuntimeError("hatena:syntax が取得できませんでした")
    return syntax.text.strip()

# =========================
# ブログ: 画像入り記事を投稿
# =========================
def post_hatena_entry(title: str, body: str, draft: bool = False) -> str:
    """
    はてなブログに記事を投稿し、作成されたエントリーURLを返す。
    """
    collection_url = f"https://blog.hatena.ne.jp/{HATENA_ID}/{HATENA_BLOG_ID}/atom/entry"  # [web:33]

    # AtomPubエントリXML（content.type は Markdown 前提なら text/x-markdown等でもOK）[web:33]
    now = datetime.now(timezone.utc)
    updated_str = format_datetime(now)  # RFC2822形式[web:33]

    draft_value = "yes" if draft else "no"

    entry_xml = f"""\
<entry xmlns="http://www.w3.org/2005/Atom"
       xmlns:app="http://www.w3.org/2007/app">
  <title>{title}</title>
  <updated>{updated_str}</updated>
  <author><name>{HATENA_ID}</name></author>
  <content type="text/plain">
{body}
  </content>
  <app:control>
    <app:draft>{draft_value}</app:draft>
  </app:control>
</entry>
"""

    resp = requests.post(
        collection_url,
        data=entry_xml.encode("utf-8"),
        auth=(HATENA_ID, HATENA_API_KEY),  # Basic認証[web:33]
        headers={"Content-Type": "application/xml"},
    )
    resp.raise_for_status()

    # 返ってきたエントリXMLから <link rel="alternate"> の href = 記事URL を取得[web:33]
    root = ET.fromstring(resp.content)
    ns = {"atom": "http://www.w3.org/2005/Atom"}
    for link in root.findall("atom:link", ns):
        if link.get("rel") == "alternate":
            return link.get("href")
    return ""

# =========================
# メイン: 画像 + タイトルで投稿
# =========================
def post_with_title_and_image(image_path: str, post_title: str) -> str:
    # 1. 画像をフォトライフへアップロードし、[f:id:...] を取得
    image_syntax = upload_to_fotolife(image_path, post_title)

    # 2. 本文を組み立て（ここではタイトル文＋画像だけ）
    body = f"{post_title}\n\n{image_syntax}\n"

    # 3. はてなブログへ投稿（即公開 draft=False）
    entry_url = post_hatena_entry(post_title, body, draft=False)
    return entry_url

if __name__ == "__main__":
    # 例: ./main.py
    image_path = "test.png"
    post_title = "テスト投稿 from Python"
    url = post_with_title_and_image(image_path, post_title)
    print("posted:", url)

