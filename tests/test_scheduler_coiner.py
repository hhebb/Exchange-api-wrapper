import unittest, configparser, inspect
from autotrading.db.mongodb import mongodb_handler
from autotrading.scheduler.coiner import Coiner
from autotrading.machine.korbit_machine import KorbitMachine

class SchedulerCoinerTestCase(unittest.TestCase):
    """
    Coiner test module
    """
    def setUp(self):
        print("setUp")
        korbit_machine = KorbitMachine()
        self.coiner = Coiner(korbit_machine)

    def test_get_ticker(self):
        """
        test get_ticker
        """
        print(inspect.stack()[0][3])
        result = self.coiner.get_ticker("xrp_krw")
        assert(result)
        print(result)

    def test_get_filled_orders_etc(self):
        """
        test get_filled_orders
        """
        print(inspect.stack()[0][3])
        result = self.coiner.get_filled_orders("etc_krw")
        assert(result)
        print(result)

    def test_get_filled_orders_btc(self):
        """
        test get_filled_orders
        """
        print(inspect.stack()[0][3])
        result = self.coiner.get_filled_orders("btc_krw")
        assert(result)
        print(result)

    def test_get_filled_orders_eth(self):
        """
        test get_filled_orders
        """
        print(inspect.stack()[0][3])
        result = self.coiner.get_filled_orders("eth_krw")
        assert(result)
        print(result)

    def test_get_filled_orders_xrp(self):
        """
        test get_filled_orders
        """
        print(inspect.stack()[0][3])
        result = self.coiner.get_filled_orders("xrp_krw")
        assert(result)
        print(result)

 
    def tearDown(self):
        pass

if __name__ == "__main__":
    unittest.main()
