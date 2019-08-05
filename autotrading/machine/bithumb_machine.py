import requests
import time
import math
from autotrading.machine.base_machine import Machine
import configparser
import json
import base64
import hashlib
import hmac
import urllib

class BithumbMachine(Machine):
    """
    빗썸 거래소와 거래를 위한 클래스입니다.
    BASE_API_URL은 REST API호출의 기본 URL입니다.
    TRADE_CURRENCY_TYPE은 빗썸에서 거래가 가능한 화폐의 종류입니다.
    """
    BASE_API_URL = "https://api.bithumb.com"
    TRADE_CURRENCY_TYPE = ["BTC", "ETH", "DASH", "LTC", "ETC", "XRP", "BCH", "XMR", "ZEC", "QTUM", "BTG", "EOS"]
    def __init__(self):
        """
        BithumbMachine 클래스의 최초 호출 메소드 입니다.
        config.ini파일에서 connect_key, secret_key, username을 읽어옵니다.
        """
        config = configparser.ConfigParser()
        config.read('conf/config.ini')
        self.CLIENT_ID = config['BITHUMB']['connect_key']
        self.CLIENT_SECRET = config['BITHUMB']['secret_key']
        self.USER_NAME = config['BITHUMB']['username']
        #self.access_token = None
        #self.refresh_token = None
        #self.token_type = None
         
    def get_username(self):
        return self.USER_NAME

    def get_token(self):
        pass
        
    def set_token(self):
        pass
        
    def get_nonce(self):
        return self.usecTime()#str(int(time.time()))

    def get_ticker(self, currency_type=None):
        """마지막 체결정보(Tick)을 얻기 위한 메소드입니다.

        Args:
            currency_type(str):화폐 종류를 입력받습니다. 화폐의 종류는 TRADE_CURRENCY_TYPE에 정의되어있습니다.
        
        Returns:
            결과를 딕셔너리로 반환합니다. 
            결과의 필드는 timestamp, last, bid, ask, high, low, volume이 있습니다.
        """
        if currency_type is None:
            raise Exception('Need to currency type')
        if currency_type not in self.TRADE_CURRENCY_TYPE:
            raise Exception('Not support currency type') 
        time.sleep(1)
        ticker_api_path = "/public/ticker/{currency}".format(currency=currency_type)
        url_path = self.BASE_API_URL + ticker_api_path
        res = requests.get(url_path)
        response_json = res.json()
        result={}
        result["timestamp"] = str(response_json['data']["date"])
        result["last"] = response_json['data']["closing_price"]
        result["bid"] = response_json['data']["buy_price"]
        result["ask"] = response_json['data']["sell_price"]
        result["high"] = response_json['data']["max_price"]
        result["low"] = response_json['data']["min_price"]
        result["volume"] = response_json['data']["volume_1day"]
        return result

    def get_filled_orders(self, currency_type=None):
        """체결정보를 얻어오기 위한 메소드입니다.
        
        Note:
            가장 최근 100개만 받을 수 있습니다.
            
        Args:
            currency_type(str):화폐 종류를 입력받습니다. 화폐의 종류는 TRADE_CURRENCY_TYPE에 정의되어있습니다.
            
        Returns:
           가장 최근 체결정보를 딕셔너리의 리스트 형태로 반환합니다. 
        """
        if currency_type is None:
            raise Exception("Need to currency_type")
        if currency_type not in self.TRADE_CURRENCY_TYPE:
            raise Exception('Not support currency type') 
        time.sleep(1)
        params = {'offset':0,'count':100}
        orders_api_path = "/public/recent_transactions/{currency}".format(currency=currency_type)
        url_path = self.BASE_API_URL + orders_api_path
        res = requests.get(url_path, params=params)
        result = res.json()
        return result

    def microtime(self, get_as_float = False):
        """nonce값을 만들때 사용할 timestamp값을 반환하는 메소드입니다.
        Args: 
            get_as_float(boolean):반환 형식을 float형식으로 반환한지 정수형으로 반환할지 여부를 전달받습니다.
            
        Returns:
             정수형이나 소수형으로 반환합니다.
        """
        if get_as_float:
            return time.time()
        else:
            return '%f %d' % math.modf(time.time())

    def usecTime(self) :
        """
        microtime을 호출하여 얻은 값을 가공하는 메소드입니다.
        
        Returns:
             Timestamp형식으로 반환합니다.
        """
        mt = self.microtime(False)
        mt_array = mt.split(" ")[:2]
        return mt_array[1] + mt_array[0][2:5]
   
    def get_signature(self, encoded_payload, secret_key):
        """
        Args: 
            encoded_payload(str): 인코딩된 payload 값입니다.
            secret_key(str): 서명할때 사용할 사용자의 secret_key 입니다.
        Returns:
            사용자의 secret_key로 서명된 데이터를 반환합니다.
        """
        signature = hmac.new(secret_key, encoded_payload, hashlib.sha512);
        api_sign = base64.b64encode(signature.hexdigest().encode('utf-8'))
        return api_sign
    
    def get_wallet_status(self, currency_type=None):
        """사용자의 지갑정보를 조회하는 메소드입니다.
        
        Args:
            currency_type(str):화폐 종류를 입력받습니다. 화폐의 종류는 TRADE_CURRENCY_TYPE에 정의되어있습니다.
            
        Returns:
            사용자의 지갑에 화폐별 잔고를 딕셔너리 형태로 반환합니다.
        """
        if currency_type is None:
            raise Exception("Need to currency_type")
        if currency_type not in self.TRADE_CURRENCY_TYPE:
            raise Exception('Not support currency type') 
        time.sleep(1)
        endpoint ="/info/balance"
        url_path = self.BASE_API_URL + endpoint
        
        endpoint_item_array = {
             "endpoint" : endpoint,
             "currency" : currency_type 
        }
        
        uri_array = dict(endpoint_item_array) # Concatenate the two arrays.
        str_data = urllib.parse.urlencode(uri_array)
        nonce = self.get_nonce()
        data = endpoint + chr(0) + str_data + chr(0) + nonce
        utf8_data = data.encode('utf-8')
        
        key = self.CLIENT_SECRET
        utf8_key = key.encode('utf-8')
       
        headers = {'Content-Type': 'application/x-www-form-urlencoded',
                   'Api-Key':self.CLIENT_ID,
                   'Api-Sign':self.get_signature(utf8_data,bytes(utf8_key)),
                   'Api-Nonce':nonce}

        res = requests.post(url_path, headers=headers, data=str_data)
        result = res.json()
        return result["data"] 

    def get_list_my_orders(self, currency_type=None):
        """사용자의 현재 예약중인 주문 현황을 조회하는 메소드입니다.
        
        Args:
            currency_type(str):화폐 종류를 입력받습니다. 화폐의 종류는 TRADE_CURRENCY_TYPE에 정의되어있습니다.
            
        Returns:
            거래 진행 중인 현황을 리스트로 반환합니다.
        """
        if currency_type is None:
            raise Exception("Need to currency_type")
        if currency_type not in self.TRADE_CURRENCY_TYPE:
            raise Exception('Not support currency type') 
        time.sleep(1)
        endpoint ="/info/orders"
        url_path = self.BASE_API_URL + endpoint
        
        endpoint_item_array = {
             "endpoint" : endpoint,
             "currency" : currency_type
        }
        
        uri_array = dict(endpoint_item_array) # Concatenate the two arrays.
        str_data = urllib.parse.urlencode(uri_array)
        nonce = self.get_nonce()
        data = endpoint + chr(0) + str_data + chr(0) + nonce
        utf8_data = data.encode('utf-8')
        
        key = self.CLIENT_SECRET
        utf8_key = key.encode('utf-8')
       
        headers = {'Content-Type': 'application/x-www-form-urlencoded',
                   'Api-Key':self.CLIENT_ID,
                   'Api-Sign':self.get_signature(utf8_data,bytes(utf8_key)),
                   'Api-Nonce':nonce}

        res = requests.post(url_path, headers=headers, data=str_data)
        result = res.json()
        return result["data"] 

    def get_my_order_status(self, currency_type=None, order_id=None):
        """사용자의 주문정보 상세정보를 조회하는 메소드입니다. 
        
        Args:
            currency_type(str):화폐 종류를 입력받습니다. 화폐의 종류는 TRADE_CURRENCY_TYPE에 정의되어있습니다.
            order_id(str): 거래ID
            
        Returns:
            order_id에 해당하는 주문의 상세정보를 반환합니다.
        """
        if currency_type is None:
            raise Exception("Need to currency_type")
        if currency_type not in self.TRADE_CURRENCY_TYPE:
            raise Exception('Not support currency type') 
        time.sleep(1)
        endpoint ="/info/order_detail"
        url_path = self.BASE_API_URL + endpoint
        
        endpoint_item_array = {
             "endpoint" : endpoint,
             "currency" : currency_type
        }
        
        uri_array = dict(endpoint_item_array) # Concatenate the two arrays.
        str_data = urllib.parse.urlencode(uri_array)
        nonce = self.get_nonce()
        data = endpoint + chr(0) + str_data + chr(0) + nonce
        utf8_data = data.encode('utf-8')
        
        key = self.CLIENT_SECRET
        utf8_key = key.encode('utf-8')
       
        headers = {'Content-Type': 'application/x-www-form-urlencoded',
                   'Api-Key':self.CLIENT_ID,
                   'Api-Sign':self.get_signature(utf8_data,bytes(utf8_key)),
                   'Api-Nonce':nonce}

        res = requests.post(url_path, headers=headers, data=str_data)
        result = res.json()
        return result["data"] 

    def buy_order(self, currency_type=None, price=None, qty=None, order_type="limit"):
        """매수 주문을 실행하는 메소드입니다.. 
        
        Note:
            화폐 종류마다 최소 주문 수량은 다를 수 있습니다.
            이 메소드는 지정가 거래만 지원합니다.      
            
        Args:
            currency_type(str):화폐 종류를 입력받습니다. 화폐의 종류는 TRADE_CURRENCY_TYPE에 정의되어있습니다.
            price(int): 1개 수량 주문에 해당하는 원화(krw) 값
            qty(float): 주문 수량입니다. 
            
        Returns:
            주문의 상태에 대해 반환합니다.
        """
        if currency_type is None:
            raise Exception("Need to currency_type")
        if currency_type not in self.TRADE_CURRENCY_TYPE:
            raise Exception('Not support currency type') 
        time.sleep(1)
        endpoint ="/trade/place"
        url_path = self.BASE_API_URL + endpoint
        
        endpoint_item_array = {
             "endpoint" : endpoint,
             "order_currency" : currency_type,
             "payment_currenct" : "KRW",
             "units" : qty,
             "price" : price,
             "type" : "bid"
        }
        
        uri_array = dict(endpoint_item_array) # Concatenate the two arrays.
        str_data = urllib.parse.urlencode(uri_array)
        nonce = self.get_nonce()
        data = endpoint + chr(0) + str_data + chr(0) + nonce
        utf8_data = data.encode('utf-8')
        
        key = self.CLIENT_SECRET
        utf8_key = key.encode('utf-8')
       
        headers = {'Content-Type': 'application/x-www-form-urlencoded',
                   'Api-Key':self.CLIENT_ID,
                   'Api-Sign':self.get_signature(utf8_data,bytes(utf8_key)),
                   'Api-Nonce':nonce}

        res = requests.post(url_path, headers=headers, data=str_data)
        result = res.json()
        return result 

    def sell_order(self, currency_type=None, price=None, qty=None, order_type="limit"):
        """매도 주문을 실행하는 메소드입니다.. 
        
        Note:
            화폐 종류마다 최소 주문 수량은 다를 수 있습니다.
            이 메소드는 지정가 거래만 지원합니다.      
            
        Args:
            currency_type(str):화폐 종류를 입력받습니다. 화폐의 종류는 TRADE_CURRENCY_TYPE에 정의되어있습니다.
            price(int): 1개 수량 주문에 해당하는 원화(krw) 값
            qty(float): 주문 수량입니다. 
            
        Returns:
            주문의 상태에 대해 반환합니다.
        """
        if currency_type is None:
            raise Exception("Need to currency_type")
        if currency_type not in self.TRADE_CURRENCY_TYPE:
            raise Exception('Not support currency type') 
        time.sleep(1)
        endpoint ="/trade/place"
        url_path = self.BASE_API_URL + endpoint
        
        endpoint_item_array = {
             "endpoint" : endpoint,
             "order_currency" : currency_type,
             "payment_currenct" : "KRW",
             "units" : qty,
             "price" : price,
             "type" : "ask"
        }
        
        uri_array = dict(endpoint_item_array) # Concatenate the two arrays.
        str_data = urllib.parse.urlencode(uri_array)
        nonce = self.get_nonce()
        data = endpoint + chr(0) + str_data + chr(0) + nonce
        utf8_data = data.encode('utf-8')
        
        key = self.CLIENT_SECRET
        utf8_key = key.encode('utf-8')
       
        headers = {'Content-Type': 'application/x-www-form-urlencoded',
                   'Api-Key':self.CLIENT_ID,
                   'Api-Sign':self.get_signature(utf8_data,bytes(utf8_key)),
                   'Api-Nonce':nonce}

        res = requests.post(url_path, headers=headers, data=str_data)
        result = res.json()
        return result

    def cancel_order(self, currency_type=None, order_type=None, order_id=None):
        """매도 주문을 실행하는 메소드입니다.. 
        
        Args:
            currency_type(str):화폐 종류를 입력받습니다. 화폐의 종류는 TRADE_CURRENCY_TYPE에 정의되어있습니다.
            order_type(str): 취소하려는 주문의 종류(매수, 매도) 
            order_id(str): 취소 주문하려는 주문의 ID
            
        Returns:
            주문의 상태에 대해 반환합니다.
        """
        if currency_type is None:
            raise Exception("Need to currency_type")
        if currency_type not in self.TRADE_CURRENCY_TYPE:
            raise Exception('Not support currency type') 
        time.sleep(1)
        endpoint ="/trade/cancel"
        url_path = self.BASE_API_URL + endpoint
        
        endpoint_item_array = {
             "endpoint" : endpoint,
             "currency" : currency_type,
             "type" : order_type,
             "order_id" : order_id
        }
        
        uri_array = dict(endpoint_item_array) # Concatenate the two arrays.
        str_data = urllib.parse.urlencode(uri_array)
        nonce = self.get_nonce()
        data = endpoint + chr(0) + str_data + chr(0) + nonce
        utf8_data = data.encode('utf-8')
        
        key = self.CLIENT_SECRET
        utf8_key = key.encode('utf-8')
       
        headers = {'Content-Type': 'application/x-www-form-urlencoded',
                   'Api-Key':self.CLIENT_ID,
                   'Api-Sign':self.get_signature(utf8_data,bytes(utf8_key)),
                   'Api-Nonce':nonce}

        res = requests.post(url_path, headers=headers, data=str_data)
        result = res.json()
        return result
        
    def __repr__(self):
        return "(Bithumb %s)"%self.USER_NAME

    def __str__(self):
        return str("Bithumb")
