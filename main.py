import chatroom
import time

bot = chatroom.WebSocket()

@bot.command(name="test")
async def test_command(*args):
    print(await bot.send_room(f"あああ"))

# イベント
@bot.event
async def on_chat(message: chatroom.Message):
    # メッセージ受信
    if message.content == "こんばんは":
        await bot.send_room("こんばんは！")
    await bot.process_command(message)

# ログイン
bot.login("efx3msmy")