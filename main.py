import chatroom
import time

bot = chatroom.WebSocket()

@bot.command(name="test")
async def test_command(ctx: chatroom.Context, *args):
    print(await ctx.room.send("こんばんは！"))

@bot.command(name="create")
async def create_command(ctx: chatroom.Context, *args):
    room = await bot.create_room()
    await ctx.room.send(room.url)
    await bot.join_room(room)

# イベント
@bot.event
async def on_chat(message: chatroom.Message):
    # メッセージ受信
    if message.content == "こんばんは":
        await message.room.send("こんばんは！")
    await bot.process_command(message)

# ログイン
hash = bot.url_to_hash("")

bot.login(hash)