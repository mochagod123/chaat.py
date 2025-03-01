import chatroom
import time

chaat = chatroom.Chaat()

# ログイン
chaat.login()

# 部屋の作成
cr = chaat.create_room()

# URLの取得
print(cr["url"])

# メッセージ送信
print(chaat.send_room(cr["hash"], "あああ"))

# メッセージ取得
print(chaat.fetch_room(cr["hash"]))