import requests
import time
from autotrading.machine.base_machine import Machine
import configparser
import base64
import json
import hashlib
import hmac

class CoinOneMachine(Machine):
    """
    코인원 거래소와 거래를 위한 클래스입니다.
    BASE_API_URL은 REST API호출의 기본 URL입니다.
    TRADE_CURRENCY_TYPE은 코인원에서 거래가 가능한 화폐의 종류입니다.
    """
    BASE_API_URL = "https://api.coinone.co.kr"
    TRADE_CURRENCY_TYPE = ["btc", "eth", "etc", "bch", "qtum", "krw", "xrp", "iota", "ltc"]
    
    def __init__(self):
        """
        CoinOneMachine 클래스의 최초 호출 메소드입니다.
        config.ini에서 access_token, secret_key 정보를 읽어옵니다.
        """
        config = configparser.ConfigParser()
        config.read('conf/config.ini')
        self.access_token = config['COINONE']['access_token']
        self.secret_key = config['COINONE']['secret_key']
        
    def get_username(self):
        if self.username is None: 
            return None
        return self.username

    def get_nonce(self):
        """Private API 호출 시 사용할 nonce값을 구하는 메소드입니다.
        
        Returns:
            nonce값을 반환합니다.
        """   
        return int(time.time())

    def get_token(self):
        """인증토큰 정보를 받기 위한 메소드입니다.
        Returns:
            인증토큰(asscee_token)이 있는 경우 반환합니다.
            
        Raises:
            access_token이 없는 경우 Exception을 발생시킵니다.
        
        """
        if self.access_token is not None:
            return self.access_token
        else:
            raise Exception("Need to set_token")

    def set_token(self, grant_type="refresh_token"):
        """인증토큰 정보를 만들기 위한 메소드입니다.
         
        Returns:
            만료시간(expire),인증토큰(access_token),리프레쉬토큰(refresh_token) 을 반환합니다.
        
        Raises:
            grant_type이 password나 refresh_token이 아닌 경우 Exception을 발생시킵니다.
        """   
        token_api_path = "/oauth/refresh_token/"
        url_path = self.BASE_API_URL + token_api_path
        self.expire = 3600

        if grant_type == "refresh_token":
            headers = {"content-type":"application/x-www-form-urlencoded"} 
            data = {"access_token":self.access_token}
            res = requests.post(url_path, headers=headers, data=data)
            result = res.json()
            if result["result"] == "success":
                config = configparser.ConfigParser()
                config.read('conf/config.ini')
                self.access_token = result["accessToken"]
                config["COINONE"]["access_token"] = self.access_token
                with open('conf/config.ini', 'w') as configfile:
                    config.write(configfile)
            else:
                raise Exception("Failed set_token")
        else:
            self.access_token = config['COINONE']['access_token']
        return self.expire, self.access_token, self.access_token

    def get_ticker(self, currency_type=None):
        """마지막 체결정보(Tick)을 얻기 위한 메소드입니다.

        Args:
            currency_type(str):화폐 종류를 입력받습니다. 화폐의 종류는 TRADE_CURRENCY_TYPE에 정의되어있습니다.
        
        Returns:
            결과를 딕셔너리로 반환합니다. 
            결과의 필드는 timestamp, last, bid, ask, high, low, volume이 있습니다.
            
        Raise:
            currency_type이 없으면 Exception을 발생시킵니다. 
        """
        ticker_api_path = '/ticker/'
        url_path = self.BASE_API_URL + ticker_api_path
        params = {"currency": currency_type}
        res = requests.get(url_path, params=params)
        response_json = res.json() 
        result = {}
        result["timestamp"] = str(response_json["timestamp"])
        result["last"] = response_json["last"]
        result["high"] = response_json["high"]
        result["low"] = response_json["low"]
        result["volume"] = response_json["volume"]
        return result

    def get_filled_orders(self, currency_type=None, per="minute"):
        pass

    def get_signature(self, encoded_payload, secret_key):
        """
        Args: 
            encoded_payload(str): 인코딩된 payload 값입니다.
            secret_key(str): 서명할때 사용할 사용자의 secret_key 입니다.
        Returns:
            사용자의 secret_key로 서명된 데이터를 반환합니다.
        """
        signature = hmac.new(secret_key, encoded_payload, hashlib.sha512);
        return signature.hexdigest()
    
    def get_encoded_payload(self, payload):
        """
        Args:
            payload(str):인코딩할 payload
             
        Returns:
            인코딩된 payload값을 반환합니다 .
        """
        dumped_json = json.dumps(payload)
        return base64.b64encode(dumped_json.encode('utf-8'))  
        
    def get_wallet_status(self):
        """사용자의 지갑정보를 조회하는 메소드입니다.
        
        Returns:
            사용자의 지갑에 화폐별 잔고를 딕셔너리 형태로 반환합니다.
        """
        time.sleep(1)
        wallet_status_api_path = "/v2/account/balance"
        url_path = self.BASE_API_URL + wallet_status_api_path
        payload ={
            "access_token":self.access_token,
            'nonce':self.get_nonce()
        }
        encoded_payload = self.get_encoded_payload(payload)
        signature = self.get_signature(encoded_payload, self.secret_key.encode('utf-8')) 
        
        headers = {'Content-type': 'application/json',
                   'X-COINONE-PAYLOAD': encoded_payload,
                   'X-COINONE-SIGNATURE': signature}

        res = requests.post(url_path, headers=headers, data=payload)
        result = res.json()
        wallet_status = {currency: result[currency] for currency in self.TRADE_CURRENCY_TYPE }
        return wallet_status

    def get_list_my_orders(self, currency_type=None):
        """사용자의 현재 예약중인 주문 현황을 조회하는 메소드입니다.
        
        Args:
            currency_type(str):화폐 종류를 입력받습니다. 화폐의 종류는 TRADE_CURRENCY_TYPE에 정의되어있습니다.
            
        Returns:
            거래 진행 중인 현황을 리스트로 반환합니다.
        """
        time.sleep(1)
        list_api_path = "/v2/order/limit_orders/"
        url_path = self.BASE_API_URL + list_api_path
        
        payload ={
            "access_token":self.access_token,
            "currency":currency_type,
            'nonce':self.get_nonce()
        }
        
        encoded_payload = self.get_encoded_payload(payload)
        signature = self.get_signature(encoded_payload, self.secret_key.encode('utf-8')) 
        
        headers = {'Content-type': 'application/json',
                   'X-COINONE-PAYLOAD': encoded_payload,
                   'X-COINONE-SIGNATURE': signature}

        res = requests.post(url_path, headers=headers, data=payload)
        result = res.json()
        return result

    def get_my_order_status(self, currency_type=None, order_id=None):
        """사용자의 주문정보 상세정보를 조회하는 메소드입니다. 
        
        Args:
            currency_type(str):화폐 종류를 입력받습니다. 화폐의 종류는 TRADE_CURRENCY_TYPE에 정의되어있습니다.
            order_id(str): 거래ID
            
        Returns:
            order_id에 해당하는 주문의 상세정보를 반환합니다.
        """
        list_api_path = "/v2/order/order_info/"
        url_path = self.BASE_API_URL + list_api_path
        
        payload ={
            "access_token":self.access_token,
            "currency":currency_type,
            "order_id":order_id,
            'nonce':self.get_nonce()
        }
        
        encoded_payload = self.get_encoded_payload(payload)
        signature = self.get_signature(encoded_payload, self.secret_key.encode('utf-8')) 
        
        headers = { 'Content-type': 'application/json',
                    'X-COINONE-PAYLOAD': encoded_payload,
                    'X-COINONE-SIGNATURE': signature }

        res = requests.post(url_path, headers=headers, data=payload)
        result = res.json()
        return result


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
        if order_type != "limit":
            raise Exception("Coinone order type support only limit.")
        time.sleep(1)
        buy_limit_api_path ="/v2/order/limit_buy/"
        url_path = self.BASE_API_URL + buy_limit_api_path
        
        payload ={
            "access_token" : self.access_token,
            "price" : int(price),
            "qty" : float(qty),
            "currency":currency_type,
            'nonce' : self.get_nonce()
        }

        encoded_payload = self.get_encoded_payload(payload)
        signature = self.get_signature(encoded_payload, self.secret_key.encode('utf-8'))
        
        headers = {'Content-type': 'application/json',
                   'X-COINONE-PAYLOAD': encoded_payload,
                   'X-COINONE-SIGNATURE': signature }

        res = requests.post(url_path, headers=headers, data=payload)
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
        if order_type != "limit":
            raise Exception("Coinone order type support only limit.")
        time.sleep(1)
        sell_limit_api_path ="/v2/order/limit_sell/"
        url_path = self.BASE_API_URL + sell_limit_api_path
        
        payload ={
            "access_token" : self.access_token,
            "price" : int(price),
            "qty" : float(qty),
            "currency":currency_type,
            'nonce' : self.get_nonce()
        }
        
        encoded_payload = self.get_encoded_payload(payload)
        signature = self.get_signature(encoded_payload, self.secret_key.encode('utf-8'))
        
        headers = {'Content-type': 'application/json',
                   'X-COINONE-PAYLOAD': encoded_payload,
                   'X-COINONE-SIGNATURE': signature }

        res = requests.post(url_path, headers=headers, data=payload)
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
        if currency_type is None or order_type is None or order_id is None:
            raise Exception("Need to parameter")
        time.sleep(1)
        cancel_api_path ="/v2/order/cancel/"
        url_path = self.BASE_API_URL + cancel_api_path
           
        payload ={
            "access_token" : self.access_token,
            "order_id" : order_id,
            "currency":currency_type,
            "is_ask": 1 if order_type is "sell" else 0,
            'nonce' : self.get_nonce()
        }
        
        encoded_payload = self.get_encoded_payload(payload)
        signature = self.get_signature(encoded_payload, self.secret_key.encode('utf-8'))
 
        headers = {'Content-type': 'application/json',
                   'X-COINONE-PAYLOAD': encoded_payload,
                   'X-COINONE-SIGNATURE': signature }

        res = requests.post(url_path, headers=headers, data=payload)
        result = res.json()
        return result

    def __repr__(self):
        return "(CoinOne %s)"%self.username

    def __str__(self):
        return str("CoinOne")
