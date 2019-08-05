import configparser
from autotrading.pusher.base_pusher import Pusher
from telethon import TelegramClient

class PushTelegram(Pusher):

    def __init__(self):
        """텔레그램으로 메시지를 보내기 위한 PushTelegram 클래스입니다.
        config.ini파일로 부터 api_id와 api_hash를 읽어옵니다. 
        TelegramClient 생성시 app name과 api_id, api_hash를 파라미터로 전달합니다.
        """
        config = configparser.ConfigParser()
        config.read('conf/config.ini')
        api_id = config['TELEGRAM']['api_id']
        api_hash = config['TELEGRAM']['api_hash']
        self.telegram = TelegramClient("auto-trading", api_id, api_hash)
        assert self.telegram
        self.telegram.connect()
        
    def send_message(self, username=None, message=None):
        """
        Args:
            username(str): 보낼 유저명
            message(str): 보낼 메시지
        """
        self.telegram.send_message(username, message)
