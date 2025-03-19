import chatroom

# Prefix指定
bot = chatroom.WebSocket(prefix=">>")

@bot.command(name="test")
async def test_command(ctx: chatroom.Context, *args):
    print(await ctx.room.send("こんばんは！"))

@bot.command(name="create")
async def create_command(ctx: chatroom.Context, *args):
    room = await bot.create_room()
    await ctx.room.send(room.url)
    await bot.join_room(room)

@bot.command(name="user")
async def user_command(ctx: chatroom.Context, *args):
    await ctx.room.send(ctx.user.name)

@bot.command(name="room")
async def user_command(ctx: chatroom.Context, *args):
    await ctx.room.send(f"Hash: {ctx.room.hash}\nURL: {ctx.room.url}")

# イベント
@bot.event
async def on_ready(room: chatroom.Room):
    print(f"起動しました。: {room.url}")

@bot.event
async def on_chat(message: chatroom.Message):
    # メッセージ受信
    if message.content == "こんばんは":
        await message.room.send("こんばんは！")
    elif message.content == "改行":
        await message.room.send(f"あ\nい")
    await bot.process_command(message)

# ログイン
hash = bot.url_to_hash("URL")

bot.login(hash)