import unittest
from autotrading.machine.coinone_machine import CoinOneMachine
import inspect

class CoinOneMachineTestCase(unittest.TestCase):
    def setUp(self):
        self.coinone_machine = CoinOneMachine()
        
    def tearDown(self):
        pass
        
    def test_set_token(self):
        print(inspect.stack()[0][3])
        expire, access_token, refresh_token = self.coinone_machine.set_token()
        assert access_token
        print(access_token)

    def test_get_wallet_status(self):
        print(inspect.stack()[0][3])
        result = self.coinone_machine.get_wallet_status()
        assert result
        print(result)
    
    def test_get_ticker(self):
        print(inspect.stack()[0][3])
        result = self.coinone_machine.get_ticker(currency_type="xrp")
        assert result
        print(result)
        
    """
    def test_buy_order(self):
        print(inspect.stack()[0][3])
        result = self.coinone_machine.buy_order(currency_type="xrp",
                                                     price="230",
                                                     qty="1",
                                                     order_type="limit")
        assert result
        print(result)
        
    def test_sell_order(self):
        print(inspect.stack()[0][3])
        result = self.coinone_machine.sell_order(currency_type="xrp",
                                                 price="230",
                                                 qty="1",
                                                 order_type="limit")
        assert result
        print(result)
        
    def test_cancel_order(self):
        print(inspect.stack()[0][3])
        result = self.coinone_machine.cancel_order(currency_type="xrp",
                                                   price="230",
                                                   qty="1",
                                                   order_type="buy",
                                                   order_id="cf68cebe-468b-4f2a-b860-3860824e5584")
        assert result
        print(result)
    """ 
    
    def test_get_list_my_orders(self):
        print(inspect.stack()[0][3])
        result = self.coinone_machine.get_list_my_orders(currency_type="xrp")
        assert result
        print(result)

    def test_get_my_order_status(self):
        print(inspect.stack()[0][3])
        result = self.coinone_machine.get_my_order_status(currency_type="xrp", order_id="60066de5-bd9f-4fcf-8381-f623d4e88101")
        assert result
        print(result)
