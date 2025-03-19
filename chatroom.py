import requests
import re
import datetime
import websockets
import ssl
import json
import time
from functools import partial
import asyncio

ssl_context = ssl.create_default_context()
ssl_context.check_hostname = False
ssl_context.verify_mode = ssl.CERT_NONE

class UserSetting():
    def __init__(self, username: str, color: str = "#000000"):
        self._username = username
        self._color = color

    @property
    def name(self):
        return self._username
    
    @property
    def color(self):
        return self._color
    
class Chaat:
    def __init__(self, hashid: str = None):
        self.ses = requests.Session()
        self.token_pat = r"[a-zA-Z0-9]{32}"
        self.token = None
        self.hash_id = hashid

    def login(self):
        res = self.ses.get("https://c.kuku.lu/")
        token = re.search(self.token_pat, res.text).group()
        self.token = token
        return True
    
    def create_room(self):
        data = {
            'action': 'createRoom',
            'csrf_token_check': self.token,
        }

        response = self.ses.post('https://c.kuku.lu/api_server.php', data=data)

        return response.json()
    
    def send_room(self, text: str, hash: str = None):
        if hash:
            data = {
                'action': 'sendData',
                'hash': hash,
                'profile_name': '匿名とむ',
                'profile_color': '#000000',
                'data': '{"type":"chat","msg":"' + text +'"}',
                'csrf_token_check': self.token,
            }

            response = self.ses.post('https://c.kuku.lu/room.php', data=data)

            return response.json()
        else:
            if not self.hash_id:
                return {"Error": "ハッシュIDが設定されていません。"}
            data = {
                'action': 'sendData',
                'hash': self.hash_id,
                'profile_name': '匿名とむ',
                'profile_color': '#000000',
                'data': '{"type":"chat","msg":"' + text +'"}',
                'csrf_token_check': self.token,
            }

            response = self.ses.post('https://c.kuku.lu/room.php', data=data)

            return response.json()
        
    def edit_user(self, usersetting: UserSetting, hash: str = None):
        if hash:
            data = {
                'action': 'changeMyProfile',
                'hash': hash,
                'new_name': usersetting.name,
                'new_trip': '',
                'new_color': usersetting.color,
                'csrf_token_check': self.token,
            }

            response = self.ses.post('https://c.kuku.lu/room.php', data=data)

            return response.json()
        else:
            if not self.hash_id:
                return {"Error": "ハッシュIDが設定されていません。"}
            data = {
                'action': 'changeMyProfile',
                'hash': self.hash_id,
                'new_name': usersetting.name,
                'new_trip': '',
                'new_color': usersetting.color,
                'csrf_token_check': self.token,
            }
            response = self.ses.post('https://c.kuku.lu/room.php', data=data)

            return response.json()
    
    def generate_current_timestamp(self):
        now = datetime.datetime.now()
        return now.strftime("%Y%m%d%H%M%S")

    def fetch_room(self, hash: str = None):
        if hash:
            data = {
                'action': 'fetchData',
                'hash': hash,
                'csrf_token_check': self.token,
                'mode': 'log',
                'type': 'last',
                'num': self.generate_current_timestamp(),
            }

            response = self.ses.post('https://c.kuku.lu/room.php', data=data)

            return response.json()
        else:
            if not self.hash_id:
                return {"Error": "ハッシュIDが設定されていません。"}
            data = {
                'action': 'fetchData',
                'hash': self.hash_id,
                'csrf_token_check': self.token,
                'mode': 'log',
                'type': 'last',
                'num': self.generate_current_timestamp(),
            }

            response = self.ses.post('https://c.kuku.lu/room.php', data=data)

            return response.json()
        
class Command:
    def __init__(self, name, func):
        self.name = name
        self.func = func

    async def invoke(self, ctx, *args):
        return await self.func(ctx, *args)

class Http:
    def __init__(self, session: requests.Session, token: str):
        self.ses = session
        self.token_pat = r"[a-zA-Z0-9]{32}"
        self.token = token
        pass

    async def create_room(self):
        loop = asyncio.get_event_loop()
        data = {
            'action': 'createRoom',
            'csrf_token_check': self.token,
        }

        response = await loop.run_in_executor(None, partial(self.ses.post, 'https://c.kuku.lu/api_server.php', data=data))

        js = response.json()

        return js

    async def send_room(self, text: str, hash: str):
        js = {"type":"chat", "msg":f"{text}"}

        loop = asyncio.get_event_loop()
        data = {
            'action': 'sendData',
            'hash': hash,
            'profile_name': '匿名とむ',
            'profile_color': '#000000',
            'data': json.dumps(js),
            'csrf_token_check': self.token,
        }

        response = await loop.run_in_executor(None, partial(self.ses.post, 'https://c.kuku.lu/room.php', data=data))
        return response.json()
        
    async def edit_user(self, usersetting: UserSetting, hash: str):
        loop = asyncio.get_event_loop()
        data = {
            'action': 'changeMyProfile',
            'hash': hash,
            'new_name': usersetting.name,
            'new_trip': '',
            'new_color': usersetting.color,
            'csrf_token_check': self.token,
        }

        response = await loop.run_in_executor(None, partial(self.ses.post, 'https://c.kuku.lu/room.php', data=data))

        return response.json()
        
    def generate_current_timestamp(self):
        now = datetime.datetime.now()
        return now.strftime("%Y%m%d%H%M%S")

    async def fetch_messages(self, hash: str):
        loop = asyncio.get_event_loop()
        data = {
            'action': 'fetchData',
            'hash': hash,
            'csrf_token_check': self.token,
                'mode': 'log',
                'type': 'last',
                'num': self.generate_current_timestamp(),
        }

        response = await loop.run_in_executor(None, partial(self.ses.post, 'https://c.kuku.lu/room.php', data=data))

        return response.json()

class Room():
    def __init__(self, hash: str):
        self._hash = hash
        pass

    async def send(self, text: str):
        return await http_req.send_room(text, self._hash)
    
    async def messages(self):
        return await http_req.fetch_messages(self._hash)
    
    async def edit_user(self, user: UserSetting):
        return await http_req.edit_user(user, self._hash)
    
    @property
    def hash(self):
        return self._hash
    
    @property
    def url(self):
        return "https://c.kuku.lu/" + self._hash

class Message():
    def __init__(self, content: str, room: Room):
        self._content = content
        self._room = room

    @property
    def content(self):
        return self._content
    
    @property
    def room(self):
        return self._room

class Context:
    def __init__(self, room: Room):
        self._room = room
        pass

    @property
    def room(self):
        return self._room

class WebSocket():
    def __init__(self, hashid: str = None):
        self.ses = requests.Session()
        self.hash_id = hashid
        self.token_pat = r"[a-zA-Z0-9]{32}"
        self.token = None
        self.events = {}
        self.commands = {}
        self.rooms = []

    def url_to_hash(self, url: str):
        return url.replace("https://c.kuku.lu", "").replace("/", "")

    def event(self, func):
        self.events[func.__name__] = func
        return func

    async def dispatch(self, event_name, *args, **kwargs):
        if event_name in self.events:
            await self.events[event_name](*args, **kwargs)

    def command(self, name=None):
        def decorator(func):
            cmd_name = name or func.__name__
            self.commands[cmd_name] = Command(cmd_name, func)
            return func
        return decorator

    async def process_command(self, message: Message):
        parts = message.content.split()
        if not parts:
            return

        cmd_name = parts[0]
        args = parts[1:]

        if cmd_name in self.commands:
            await self.commands[cmd_name].invoke(Context(message.room), *args)
        else:
            return

    async def receive_messages(self, mat: str, hash_: str):
        async with websockets.connect("wss://ws-c.kuku.lu:21004/") as websocket:
            await websocket.send(f"@{json.dumps({
                            "type": "join",
                            "room": hash_,
                            "cookie_token": mat,
                            "name": "ああああ#1030"
                        })}")
            while True:
                message = await websocket.recv()
                data = json.loads(message.replace("@", "", 1))
                if data["type"] == "data":
                    d = data["data"]
                    if d["type"] == "chat":
                        msg = d["msg"]
                        await self.dispatch("on_chat", Message(msg, Room(hash_)))

    def login(self, hashid: str = None):
        res = self.ses.get("https://c.kuku.lu/")
        token = re.search(self.token_pat, res.text).group()
        self.token = token
        global http_req
        http_req = Http(self.ses, self.token)
        if hashid:
            self.hash_id = hashid
        if self.hash_id:
            ses = requests.Session()
            j = ses.get(f"https://c.kuku.lu/{self.hash_id}").text
            pattern = r"[a-zA-Z0-9+/=]{88}"
            matches = re.findall(pattern, j)[1]
            asyncio.run(self.receive_messages(matches, self.hash_id))
        else:
            if hashid:
                ses = requests.Session()
                j = ses.get(f"https://c.kuku.lu/{hashid}").text
                pattern = r"[a-zA-Z0-9+/=]{88}"
                matches = re.findall(pattern, j)[1]
                asyncio.run(self.receive_messages(matches, hashid))
            else:
                return "エラー"

    async def join_room(self, room: Room):
        loop = asyncio.get_event_loop()
        res = await loop.run_in_executor(None, partial(self.ses.post, "https://c.kuku.lu/"))
        token = re.search(self.token_pat, res.text).group()
        self.token = token
        j = await loop.run_in_executor(None, partial(self.ses.post, f"https://c.kuku.lu/{room.hash}"))
        pattern = r"[a-zA-Z0-9+/=]{88}"
        matches = re.findall(pattern, j.text)[1]
        await self.receive_messages(matches, room.hash)

    async def fetch_rooms(self):
        return self.rooms
    
    async def fetch_room(self, hash: str):
        return Room(hash)

    async def create_room(self):
        croom = await http_req.create_room()
        self.rooms.append(Room(croom["hash"]))
        return Room(croom["hash"])