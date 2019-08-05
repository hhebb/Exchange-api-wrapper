import unittest
from autotrading.machine.bithumb_machine import BithumbMachine
import inspect

class BithumbMachineTestCase(unittest.TestCase):

    def setUp(self):
        self.bithumb_machine = BithumbMachine()
        
    def test_get_ticker(self):
        print(inspect.stack()[0][3])
        ticker = self.bithumb_machine.get_ticker("ETC")
        assert ticker
        print(ticker)
        
    def test_get_filled_orders(self):
        print(inspect.stack()[0][3])
        ticker = self.bithumb_machine.get_filled_orders("ETC")
        assert ticker
        print(ticker)
        
    def test_get_wallet_status(self):
        print(inspect.stack()[0][3])
        result = self.bithumb_machine.get_wallet_status("ETH")
        assert result 
        print(result)
        
    def test_get_list_my_orders(self):
        print(inspect.stack()[0][3])
        result = self.bithumb_machine.get_list_my_orders("ETH")
        assert result 
        print(result)         
        
    def test_buy_order(self):
        print(inspect.stack()[0][3])
        result = self.bithumb_machine.buy_order("ETH", 1, 700000)
        assert result 
        print(result)         
        
    def test_sell_order(self):
        print(inspect.stack()[0][3])
        result = self.bithumb_machine.sell_order("ETH", 1, 1200000)
        assert result 
        print(result)         
        
    def test_cancel_order(self):
        print(inspect.stack()[0][3])
        result = self.bithumb_machine.cancel_order("ETH", "bid", "12345")
        assert result 
        print(result)         
      
    def tearDown(self):
        pass

