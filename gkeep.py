import gkeepapi

EMAIL = "m1104m@gmail.com" 
MASTER_TOKEN = "aas_et/AKppINYKxApxPN7fNKW84r3yL41RoMcxrhSMvNwX3Nl3anDvZZp4znq4n3deb_POPdGqBL14DNjeK9WxeeU66FHY4UpJwaGc-G_bMKtuq15Y2zaJs0Kf2jB0jpyc0_oTRNiCUs8l620zFnFMa_OK0RJUCZgI9CceUypVYNyCICCkCvaegGLL55SF5aiirjO3TtR_4YFxopIwNUmag1CU270=" 
NOTE_ID = "11WmRdw7CkzJKNd3jpzXj_MKePjjnGtdSFQq7a9cefZIElugWd3L6MK1byYLWZg"

keep = gkeepapi.Keep()

# 認証
keep.authenticate(EMAIL, MASTER_TOKEN)
keep.sync()  # ノート同期[web:5]

# IDからノート取得
note = keep.get(NOTE_ID)
if note is None:
    print("指定したIDのメモが見つかりませんでした。")
    exit(1)

# 未チェックの項目だけを抽出
unchecked_items = []
for item in note.items:  # チェックリストの各行にアクセス[web:32][web:96]
    if not item.checked:
        unchecked_items.append(item.text)

print(note.title)
for t in unchecked_items:
    print("[ ]", t)

