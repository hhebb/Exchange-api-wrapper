import configparser
from datetime import datetime
from celery import Celery, Task
from autotrading.db.mongodb import MongoDBHandler
from autotrading.machine import KorbitMachine

app = Celery('currency_info', backend='redis://localhost:6379/0', broker='redis://localhost:6379/0')


app.conf.beat_schedule = {
    'add-every-1-min': {
        'task': 'scheduler_currency_price.get_currency_info',
        'schedule': 60.0,
        'args':(),
    },
}

@app.task
def get_currency_info():
    korbit = KorbitMachine()
    result_etc = korbit.get_filled_orders(currency_type="etc_krw")
    result_eth = korbit.get_filled_orders(currency_type="eth_krw")
    result_btc = korbit.get_filled_orders(currency_type="btc_krw")
    result_xrp = korbit.get_filled_orders(currency_type="xrp_krw")
    result_bch = korbit.get_filled_orders(currency_type="bch_krw")
    result_btg = korbit.get_filled_orders(currency_type="btg_krw")
    mongodb = MongoDBHandler("local", "coiner", "price_info")
    result_list = result_etc + result_eth + result_btc + result_xrp + result_bch + result_btg
    if len(result_list) != 0:
        for item in result_list:
            d = datetime.fromtimestamp(item["timestamp"]/1000)
            item["year"] = d.year
            item["month"] = d.month
            item["day"] = d.day
            item["hour"] = d.hour
            item["minute"] = d.minute
            item["second"] = d.second
            item["amount"] = float(item["amount"])
            item["timestamp"] = item["timestamp"]/1000
            item.pop("tid")
        ids = mongodb.insert_items(result_list)

