import requests
import time
from autotrading.machine.base_machine import Machine
import configparser

class KorbitMachine(Machine):
    """
    코빗 거래소와 거래를 위한 클래스입니다.
    BASE_API_URL은 REST API호출의 기본 URL입니다.
    TRADE_CURRENCY_TYPE은 코빗에서 거래가 가능한 화폐의 종류입니다.
    """
    BASE_API_URL = "https://api.korbit.co.kr"
    TRADE_CURRENCY_TYPE = ["btc", "bch", "btg", "eth", "etc", "xrp", "krw"]
    
    def __init__(self):
        """
        KorbitMachine 클래스의 최초 호출 메소드입니다.
        config.ini에서 client_id, client_secret, username, password 정보를 읽어옵니다.
        """
        config = configparser.ConfigParser()
        config.read('conf/config.ini')
        self.CLIENT_ID = config['KORBIT']['client_id']
        self.CLIENT_SECRET = config['KORBIT']['client_secret']
        self.USER_NAME = config['KORBIT']['username']
        self.PASSWORD = config['KORBIT']['password']
        self.access_token = None
        self.refresh_token = None
        self.token_type = None
         
    def get_username(self):
        return self.USER_NAME

    def get_nonce(self):
        """Private API 호출 시 사용할 nonce값을 구하는 메소드입니다.
        
        Returns:
            nonce값을 반환합니다.
        """
        return str(int(time.time()))

    def get_token(self):
        """액세스토큰 정보를 받기 위한 메소드입니다.
        Returns:
            인증토큰(asscee_token)이 있는 경우 반환합니다.
            
        Raises:
            access_token이 없는 경우 Exception을 발생시킵니다.
        """
         
        if self.access_token is not None:
            return self.access_token
        else:
            raise Exception("Need to set_token")

    def set_token(self, grant_type="password"):
        """액세스토큰 정보를 만들기 위한 메소드입니다.
         
        Returns:
            만료시간(expire),인증토큰(access_token),리프레쉬토큰(refresh_token) 을 반환합니다.
        
        Raises:
            grant_type이 password나 refresh_token이 아닌 경우 Exception을 발생시킵니다.
        """
        token_api_path = "/v1/oauth2/access_token"

        url_path = self.BASE_API_URL + token_api_path
        if grant_type == "password":
            data = {"client_id":self.CLIENT_ID,
                    "client_secret":self.CLIENT_SECRET,
                    "username":self.USER_NAME,
                    "password":self.PASSWORD,
                    "grant_type":grant_type}
        elif grant_type == "refresh_token":
            data = {"client_id":self.CLIENT_ID,
                    "client_secret":self.CLIENT_SECRET,
                    "refresh_token":self.refresh_token,
                    "grant_type":grant_type}
        else:
            raise Exception("Unexpected grant_type")

        res = requests.post(url_path, data=data)
        result = res.json()
        self.access_token = result["access_token"]
        self.token_type = result["token_type"]
        self.refresh_token = result["refresh_token"]
        self.expire = result["expires_in"]
        return self.expire, self.access_token, self.refresh_token

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
        if currency_type is None:
            raise Exception('Need to currency type')
        time.sleep(1)
        params = {'currency_pair':currency_type}
        ticker_api_path = "/v1/ticker/detailed"
        url_path = self.BASE_API_URL + ticker_api_path
        res = requests.get(url_path, params=params)
        response_json = res.json()
        result={}
        result["timestamp"] = str(response_json["timestamp"])
        result["last"] = response_json["last"]
        result["bid"] = response_json["bid"]
        result["ask"] = response_json["ask"]
        result["high"] = response_json["high"]
        result["low"] = response_json["low"]
        result["volume"] = response_json["volume"]
        return result

    def get_filled_orders(self, currency_type=None, per="minute"):
        """체결정보를 얻어오기 위한 메소드입니다.
        
        Args:
            currency_type(str):화폐 종류를 입력받습니다. 화폐의 종류는 TRADE_CURRENCY_TYPE에 정의되어있습니다.
            per(str): minute, hour, day로 체결정보를 받아올 시간을 지정합니다.
            
        Returns:
           가장 최근 체결정보를 딕셔너리의 리스트 형태로 반환합니다. 
        """
        if currency_type is None:
            raise Exception("Need to currency_type")
        time.sleep(1)
        params = {'currency_pair':currency_type,'time':per}
        orders_api_path = "/v1/transactions"
        url_path = self.BASE_API_URL + orders_api_path
        res = requests.get(url_path, params=params)
        result = res.json()
        return result

    def get_constants(self):
        time.sleep(1)
        constants_api_path = "/v1/constants"
        url_path = self.BASE_API_URL + constants_api_path
        res = requests.get(url_path)
        result = res.json()
        self.constants = result
        return result

    def get_wallet_status(self):
        """사용자의 지갑정보를 조회하는 메소드입니다.
        
        Returns:
            사용자의 지갑에 화폐별 잔고를 딕셔너리 형태로 반환합니다.
        """
        time.sleep(1)
        wallet_status_api_path ="/v1/user/balances"
        url_path = self.BASE_API_URL + wallet_status_api_path
        headers = {"Authorization":"Bearer " + self.access_token}
        res = requests.get(url_path, headers=headers)
        result = res.json()
        wallet_status = { currency:dict(avail=result[currency]["available"]) for currency in self.TRADE_CURRENCY_TYPE }
        for item in self.TRADE_CURRENCY_TYPE:
            wallet_status[item]["balance"] = str(float(result[item]["trade_in_use"]) + float(result[item]["withdrawal_in_use"]))
        return wallet_status

    def get_list_my_orders(self, currency_type=None):
        """사용자의 지갑정보를 조회하는 메소드입니다.
        
        Args:
            currency_type(str):화폐 종류를 입력받습니다. 화폐의 종류는 TRADE_CURRENCY_TYPE에 정의되어있습니다.
            
        Returns:
            사용자의 지갑에 화폐별 잔고를 딕셔너리 형태로 반환합니다.
        """
        if currency_type is None:
            raise Exception("Need to currency_type")
        time.sleep(1)
        params = {'currency_pair':currency_type}
        list_order_api_path = "/v1/user/orders/open"
        url_path = self.BASE_API_URL + list_order_api_path
        headers = {"Authorization":"Bearer " + self.access_token}
        res = requests.get(url_path, headers=headers, params=params)
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
        if currency_type is None or order_id is None:
            raise Exception("Need to currency_pair and order id")
        time.sleep(1)
        list_transaction_api_path = "/v1/user/orders"
        url_path = self.BASE_API_URL + list_transaction_api_path
        headers = {"Authorization":"Bearer " + self.access_token}
        params = {"currency_pair" : currency_type, "id": order_id}
        res = requests.get(url_path, headers=headers, params=params)
        result = res.json()
        return result

    def buy_order(self, currency_type=None, price=None, qty=None, order_type="limit"):
        """매수 주문을 실행하는 메소드입니다. 
        
        Note:
            화폐 종류마다 최소 주문 수량은 다를 수 있습니다.
            이 메소드는 지정가 거래만 지원합니다.      
            
        Args:
            currency_type(str):화폐 종류를 입력받습니다. 화폐의 종류는 TRADE_CURRENCY_TYPE에 정의되어있습니다.
            price(str): 1개 수량 주문에 해당하는 원화(krw) 값
            qty(str): 주문 수량입니다. 
            
        Returns:
            주문의 상태에 대해 반환합니다.
        """   
        time.sleep(1)
        if currency_type is None or price is None or qty is None:
            raise Exception("Need to param")
        buy_order_api_path = "/v1/user/orders/buy"
        url_path = self.BASE_API_URL + buy_order_api_path
        headers = {"Authorization":"Bearer " + self.access_token}
        data = {"currency_pair":currency_type,
                "type":order_type,
                "price":price,
                "coin_amount":qty,
                "nonce":self.get_nonce()}
        res = requests.post(url_path, headers=headers, data=data)
        result = res.json()
        return result

    def sell_order(self, currency_type=None, price=None, qty=None, order_type="limit"):
        """매도 주문을 실행하는 메소드입니다. 
        
        Note:
            화폐 종류마다 최소 주문 수량은 다를 수 있습니다.
            이 메소드는 지정가 거래만 지원합니다.      
            
        Args:
            currency_type(str):화폐 종류를 입력받습니다. 화폐의 종류는 TRADE_CURRENCY_TYPE에 정의되어있습니다.
            price(str): 1개 수량 주문에 해당하는 원화(krw) 값
            qty(str): 주문 수량입니다. 
            
        Returns:
            주문의 상태에 대해 반환합니다.
        """   
        time.sleep(1)
        if price is None or qty is None or currency_type is None:
            raise Exception("Need to params")
        if order_type != "limit":
            raise Exception("Check order type")
        sell_order_api_path = "/v1/user/orders/sell"
        url_path = self.BASE_API_URL + sell_order_api_path
        headers = {"Authorization":"Bearer " + self.access_token}
        data = {"currency_pair":currency_type,
                "type":order_type,
                "price":price,
                "coin_amount":qty,
                "nonce":self.get_nonce()}
        res = requests.post(url_path, headers=headers, data=data)
        result = res.json()
        return result

    def cancel_order(self, currency_type=None, order_id=None):
        """취소 주문을 실행하는 메소드입니다.
        
        Args:
            currency_type(str):화폐 종류를 입력받습니다. 화폐의 종류는 TRADE_CURRENCY_TYPE에 정의되어있습니다.
            order_id(str): 취소 주문하려는 주문의 ID
            
        Returns:
            주문의 상태에 대해 반환합니다.
        """
        time.sleep(1)
        if currency_type is None or order_id is None:
            raise Exception("Need to params")
        cancel_order_api_path = "/v1/user/orders/cancel"
        url_path = self.BASE_API_URL + cancel_order_api_path
        headers = {"Authorization":"Bearer " + self.access_token}
        data = {"currency_pair":currency_type,
                "id":order_id,
                "nonce":self.get_nonce()}
        res = requests.post(url_path, headers=headers, data=data)
        result = res.json()
        return result

    def __repr__(self):
        return "(Korbit %s)"%self.USER_NAME

    def __str__(self):
        return str("Korbit")
