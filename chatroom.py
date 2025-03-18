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
    
class Message():
    def __init__(self, content: str):
        self._content = content

    @property
    def content(self):
        return self._content
    
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

    async def invoke(self, *args):
        return await self.func(*args)

class WebSocket():
    def __init__(self, hashid: str = None):
        self.ses = requests.Session()
        self.hash_id = hashid
        self.token_pat = r"[a-zA-Z0-9]{32}"
        self.token = None
        self.events = {}
        self.commands = {}

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

    async def process_command(self, message):
        parts = message.content.split()
        if not parts:
            return

        cmd_name = parts[0]
        args = parts[1:]

        if cmd_name in self.commands:
            await self.commands[cmd_name].invoke(*args)
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
                        await self.dispatch("on_chat", Message(msg))

    def login(self, hashid: str = None):
        res = self.ses.get("https://c.kuku.lu/")
        token = re.search(self.token_pat, res.text).group()
        self.token = token
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
            
    async def send_room(self, text: str, hash: str = None):
        loop = asyncio.get_event_loop()
        if hash:
            data = {
                'action': 'sendData',
                'hash': hash,
                'profile_name': '匿名とむ',
                'profile_color': '#000000',
                'data': '{"type":"chat","msg":"' + text +'"}',
                'csrf_token_check': self.token,
            }

            response = await loop.run_in_executor(None, partial(self.ses.post, 'https://c.kuku.lu/room.php', data=data))

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

            response = await loop.run_in_executor(None, partial(self.ses.post, 'https://c.kuku.lu/room.php', data=data))

            return response.json()
        
    async def edit_user(self, usersetting: UserSetting, hash: str = None):
        loop = asyncio.get_event_loop()
        if hash:
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
            response = await loop.run_in_executor(None, partial(self.ses.post, 'https://c.kuku.lu/room.php', data=data))

            return response.json()
        
    def generate_current_timestamp(self):
        now = datetime.datetime.now()
        return now.strftime("%Y%m%d%H%M%S")

    async def fetch_room(self, hash: str = None):
        loop = asyncio.get_event_loop()
        if hash:
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

            response = await loop.run_in_executor(None, partial(self.ses.post, 'https://c.kuku.lu/room.php', data=data))

            return response.json()