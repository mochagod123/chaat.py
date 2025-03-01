import requests
import re
import datetime
import ssl

ssl_context = ssl.create_default_context()
ssl_context.check_hostname = False
ssl_context.verify_mode = ssl.CERT_NONE

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