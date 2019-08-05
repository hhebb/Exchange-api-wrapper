import unittest
from autotrading.pusher.telegram import PushTelegram

class TestTelegram(unittest.TestCase):

    def setUp(self):
        self.pusher = PushTelegram()

    def test_send_message(self):
        self.pusher.send_message("me", "This is the 테스트 msg")

    def tearDown(self):
        pass

if __name__ == "__main__":
    unittest.main()
