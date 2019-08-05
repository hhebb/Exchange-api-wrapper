import unittest
from autotrading.machine.korbit_machine import KorbitMachine
import inspect

class KorbitMachineTestCase(unittest.TestCase):

    def setUp(self):
        self.korbit_machine = KorbitMachine()
        self.korbit_machine.set_token()
        
    def test_set_token(self):
        print(inspect.stack()[0][3])
        expire, access_token, refresh_token = self.korbit_machine.set_token(grant_type="password")
        assert expire and access_token and refresh_token
        print("Expire:", expire, "Access_token:", access_token, "Refresh_token:", refresh_token)

    def test_get_token(self):
        print(inspect.stack()[0][3])
        self.korbit_machine.set_token(grant_type="password")
        access_token = self.korbit_machine.get_token()
        assert access_token
        print(access_token)
        
    def test_get_ticker(self):
        print(inspect.stack()[0][3])
        ticker = self.korbit_machine.get_ticker("etc_krw")
        assert ticker
        print(ticker)

    def test_get_filled_orders(self):
        print(inspect.stack()[0][3])
        order_book = self.korbit_machine.get_filled_orders(currency_type="btc_krw")
        assert order_book
        print(order_book)

    def test_get_constants(self):
        print(inspect.stack()[0][3])
        constants = self.korbit_machine.get_constants()
        assert constants
        print(constants)

    def test_get_wallet_status(self):
        print(inspect.stack()[0][3])
        wallet_status = self.korbit_machine.get_wallet_status()
        assert wallet_status
        print(wallet_status)
        #print("balance:"+wallet_status["krw"]["avail"])

    def test_get_list_my_orders(self):
        print(inspect.stack()[0][3])
        my_orders = self.korbit_machine.get_list_my_orders("etc_krw")
        assert my_orders
        print(my_orders)

    def test_get_my_order_status(self):
        print(inspect.stack()[0][3])
        my_order = self.korbit_machine.get_my_order_status("etc_krw", "8100321")
        assert my_order
        print(my_order)

    def test_cacnel_order(self):
        print(inspect.stack()[0][3])
        cancel_order = self.korbit_machine.cancel_order(currency_type="etc_krw", order_id="5064611")
        assert cancel_order
        print(cancel_order)

    def test_buy_order(self):
        print(inspect.stack()[0][3])
        buy_order = self.korbit_machine.buy_order(currency_type="etc_krw", price="15000", qty="1", order_type="limit")
        assert buy_order
        print(buy_order)
        
    def test_sell_order(self):
        print(inspect.stack()[0][3])
        sell_order = self.korbit_machine.sell_order(currency_type="etc_krw", price="40000", qty="1", order_type="limit")
        assert sell_order
        print(sell_order)

    def test_get_nonce(self):
        print(inspect.stack()[0][3])
        nonce = self.korbit_machine.get_nonce()
        assert nonce
        print(nonce)
        
    def tearDown(self):
        pass

if __name__ == "__main__":
    print("test_korbit_machine")
    unittest.main()
