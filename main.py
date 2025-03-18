import chatroom
import time

bot = chatroom.WebSocket()

# イベント
@bot.event
async def on_chat(message: chatroom.Message):
    # メッセージ受信
    if message.content == "こんばんは":
        await bot.send_room("こんばんは！")
    print(message)

# ログイン

bot.login("ハッシュID")