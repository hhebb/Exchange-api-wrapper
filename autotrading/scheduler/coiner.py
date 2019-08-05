from datetime import datetime
from autotrading.machine.base_machine import Machine

class Coiner:
    """
    Coiner module class
    """
    def __init__(self, machine=None):
        if machine is None:
            raise Exception("Need to machine object")
        if not isinstance(machine, Machine):
            raise Exception("It's not a Machine subclass")
        self.machine = machine
        #self.machine.get_token()

    def get_ticker(self, currency_pair=None, request_type="detailed"):
        if currency_pair is None:
            return None
        result = self.machine.get_ticker(currency_pair=currency_pair, request_type=request_type)
        result["coin"] = currency_pair
        result["timestamp"] = result["timestamp"]/1000
        return result

    def get_filled_orders(self, currency_pair=None, time="minute"):
        if currency_pair is None:
            return None
        result = self.machine.get_filled_orders(currency_pair, time)
        for item in result:
            item["coin"] = currency_pair
            item["timestamp"] = item["timestamp"]/1000
            d = datetime.fromtimestamp(item["timestamp"])
            item["year"] = d.year
            item["month"] = d.month
            item["day"] = d.day
            item["hour"] = d.hour
            item["minute"] = d.minute
            item["second"] = d.second
            item["amount"] = float(item["amount"])
        return result
