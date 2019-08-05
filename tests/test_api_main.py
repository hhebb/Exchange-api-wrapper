import os
import api_main
import unittest
import tempfile
import json
import inspect

class FlaskrTestCase(unittest.TestCase):

    def setUp(self):
        self.db_fd, api_main.app.config['DATABASE'] = tempfile.mkstemp()
        api_main.app.config['TESTING'] = True
        self.app = api_main.app.test_client()

    def tearDown(self):
        os.close(self.db_fd)

    def test_api_coin_price_info(self):
        print(inspect.stack()[0][3])
        rv = self.app.get('/api/coin/btc_krw/price_info', query_string={"from":1507726949, "to":1507727033})
        self.assertEqual(rv.status, "200 OK")
        #print(json.loads(rv.data.decode()))

    def test_api_coin_price_info_span(self):
        print(inspect.stack()[0][3])
        rv = self.app.get('/api/coin/btc_krw/price_info', query_string={"from":1507720949, "to":1507727033, "span":"minute"})
        self.assertEqual(rv.status, "200 OK")
        #print(json.loads(rv.data.decode()))