import chatroom
import time

bot = chatroom.WebSocket("whcxw272")

@bot.event
async def on_chat(message: chatroom.Message):
    if message.content == "こんばんは":
        await bot.send_room("こんばんは！")
    print(message)

bot.login()