from autotrading.strategy.base_strategy import Strategy
from autotrading.machine.korbit_machine import KorbitMachine
from autotrading.machine.coinone_machine import CoinOneMachine
from autotrading.db.mongodb.mongodb_handler import MongoDBHandler
from autotrading.pusher.slack import PushSlack
import configparser, datetime, traceback, sys
from autotrading.logger import get_logger
import redis

logger = get_logger("step_trade")

class StepTrade(Strategy):
     
    def __init__(self, machine=None, db_handler=None, strategy=None, currency_type=None, pusher=None):
        if machine is None or db_handler is None or currency_type is None or strategy is None:
            raise Exception("Need to machine, db, currecy type, strategy")
        if isinstance(machine, KorbitMachine):
            logger.info("Korbit machine")
            self.currency_type = currency_type + "_krw"
        elif isinstance(machine, CoinOneMachine):
            logger.info("CoinOne machine")
        self.machine = machine
        self.pusher = pusher
        self.db_handler = db_handler
        result = self.db_handler.find_item({"name":strategy},"trader","trade_strategy")
        self.params = result
        #prevent token call
        if self.params["is_active"]=="inactive":
            logger.info("inactive")
            return 
        self.redis = redis.StrictRedis(host='localhost', port=6379, db=0)
        self.token = self.redis.get(str(self.machine)+self.machine.get_username())

        if self.token == None:
            logger.info("set new token")
            saved_refresh_token = self.redis.get(str(self.machine)+self.machine.get_username()+"refresh")
            if saved_refresh_token is None:
                expire, token, refresh = self.machine.set_token(grant_type="password")
            else:
                self.machine.refresh_token = saved_refresh_token.decode("utf-8")
                expire, token, refresh = self.machine.set_token(grant_type="refresh_token")
            self.redis.set(str(self.machine)+self.machine.get_username(), token, expire)
            self.redis.set(str(self.machine)+self.machine.get_username()+"refresh", refresh, 3500)
            self.token = token
        else:
            self.token = self.token.decode("utf-8")
            self.machine.access_token = self.token

        logger.info(self.token)
        logger.info(self.currency_type)
        last = self.machine.get_ticker(self.currency_type)
        self.last_val=int(last["last"])
        self.last_24h_volume = float(last["volume"])

    def scenario(self):
        now = datetime.datetime.now()
        five_min_ago = now - datetime.timedelta(minutes=5)
        five_min_ago_timestamp = int(five_min_ago.timestamp())
        pipeline_5m = [{"$match":{"timestamp":{"$gt":five_min_ago_timestamp}, "coin":self.currency_type}},
                           {"$group":{"_id":"$coin",
                                      "min_val":{"$min":"$price"},
                                      "max_val":{"$max":"$price"},
                                      "sum_val":{"$sum":"$amount"}
                    }}]

        """
        MongoDB에 화폐 데이터를 쌓고 있어야 아래 로직 사용 가능합니다.
        five_min_result = self.db_handler.aggregate(pipeline_5m)
        for item in five_min_result:
            five_max_val = int(item["max_val"])
            five_min_val = int(item["min_val"])
            five_sum_avg_val = int(item["sum_val"])/5

        if float(five_min_val) > float(self.last_val) and float(five_sum_avg_val) > float(self.last_24h_volume)/1440:
            self.pusher.send_message("#push", "down stream 5min min_val={0}, last_val{1}".format(str(five_min_val),str(self.last_val)))
            return
        if float(five_max_val) < float(self.last_val) and float(five_sum_avg_val) > float(self.last_24h_volume)/1440:
            self.pusher.send_message("#push", "up stream 5min min_val={0}, last_val{1}".format(str(five_min_val),str(self.last_val)))
        """

        logger.info("buy_price:"+str(self.last_val))
        my_orders = self.db_handler.find_items({"currency":self.currency_type, "$or":[{"status":"BUY_ORDERED"},{"status":"SELL_ORDERED"},{"status":"BUY_COMPLETED"}],
                                                                    "buy":{"$gte": self.last_val-int(self.params["step_value"]),
                                                                            "$lte": self.last_val+int(self.params["step_value"])}},"trader","trade_status")
        if my_orders.count() > 0:
            logger.info("Exists order in same price")
            for order in my_orders:
                logger.info("order:"+str(order))
        else:
            logger.info("Buy Order")
            self.item={"buy":str(self.last_val), "buy_amount":self.params["buy_amount"], "currency":self.currency_type}
            self.item["desired_value"] = int(self.last_val+int(self.params["target_profit"])/float(self.params["buy_amount"]))
            logger.info(self.item)
            wallet = self.machine.get_wallet_status()
            if int(wallet["krw"]["avail"]) > int(self.last_val*float(self.params["buy_amount"])):
                self.order_buy_transaction(machine=self.machine,
                                           db_handler=self.db_handler,
                                           currency_type=self.currency_type,
                                           item=self.item)
                #self.pusher.send_message("#push", "buy_ordered"+str(self.item))
                logger.info("buy transaction")
                self.check_buy_ordered()
            else:
                logger.info("krw is short")

    def check_buy_ordered(self):
        buy_orders = self.db_handler.find_items({"currency":self.currency_type,"status":"BUY_ORDERED"}, "trader", "trade_status")

        for item in buy_orders:
            logger.info(item)
            order_result = self.machine.get_my_order_status(self.currency_type, order_id=item["buy_order_id"])
            logger.info(order_result)
            if len(order_result)>0 and order_result[0]["status"]=="filled" and order_result[0]["price"] == str(item["buy"]):
                order_result_dict = order_result[0]
                real_buy_amount = float(order_result_dict["filled_amount"])-float(order_result_dict["fee"])
                real_buy_value = float(order_result_dict["avg_price"])
                buy_completed_time = int(order_result_dict["last_filled_at"]/1000)
                fee = float(order_result_dict["fee"])
                if order_result_dict["side"] == "bid":
                    self.update_trade_status(db_handler=self.db_handler,
                                             item_id={"_id":item["_id"]},
                                             value={"status":"BUY_COMPLETED",
                                              "real_buy_amount":real_buy_amount,
                                              "buy_completed_time":buy_completed_time,
                                              "real_buy_value":real_buy_value,
                                              "buy_fee":fee,
                                              "error":"success"})
                    #self.pusher.send_message("#push", "buy_completed:"+str(item))
            elif len(order_result)>0 and order_result[0]["status"] =="unfilled" and order_result[0]["price"] == str(item["buy"]):
                if int(item["buy"])+int(self.params["step_value"]) <= self.last_val:
                    logger.info("CancelOrder")
                    logger.info(item)
                    try:
                        self.order_cancel_transaction(machine=self.machine, db_handler=self.db_handler, currency_type=self.currency_type, item=item)
                    except:
                        error = traceback.format_exc()
                        logger.info(error)
                        self.update_trade_status(db_handler=self.db_handler,
                                                    item_id={"_id":item["_id"]},
                                                    value={"error": "failed"})
                        self.pusher.send_message("#push", "err cancle:"+str(item))
            elif len(order_result) == 0:
                self.update_trade_status(db_handler=self.db_handler,
                                            item_id={"_id":item["_id"]},
                                            value={"status":"CANCEL_ORDERED"})
    def check_buy_completed(self):
        buy_completed = self.db_handler.find_items({"currency":self.currency_type, "status":"BUY_COMPLETED"}, "trader", "trade_status")
        logger.info("BUY_COMPLETED") 
        for item in buy_completed:
            logger.info(item)
            try:
                self.order_sell_transaction(machine=self.machine, db_handler=self.db_handler, currency_type=self.currency_type, item=item)
                #self.pusher.send_message("#push", "sell_ordered:"+str(item))
            except:
                error = traceback.format_exc()
                logger.info(error)
                self.update_trade_status(db_handler=self.db_handler,
                                        item_id={"_id":item["_id"]},
                                        value={"error":"failed"})

    def check_sell_ordered(self):
        sell_orders = self.db_handler.find_items({"currency":self.currency_type,"status":"SELL_ORDERED"}, "trader", "trade_status")
        for item in sell_orders:
            logger.info(item)
            if "sell_order_id" in item:
                order_result = self.machine.get_my_order_status(self.currency_type, item["sell_order_id"])
                if order_result is not None:
                    logger.info(order_result) 
                else:
                    continue
            if len(order_result) > 0 and order_result[0]["status"]=="filled" and order_result[0]["price"] == str(item["desired_value"]):
                order_result_dict = order_result[0]
                real_sell_amount = float(order_result_dict["filled_amount"])
                real_sell_value = float(order_result_dict["avg_price"])
                completed_time = int(order_result_dict["last_filled_at"]/1000)
                fee = float(order_result_dict["fee"])
                if order_result_dict["side"] == "ask":
                    self.update_trade_status(db_handler=self.db_handler,
                                             item_id={"_id":item["_id"]},
                                             value={"status":"SELL_COMPLETED",
                                             "real_sell_amount":real_sell_amount,
                                             "sell_completed_time":completed_time,
                                             "real_sell_value":real_sell_value,
                                             "sell_fee":fee})
                    self.pusher.send_message("#push", "sell_completed:"+str(item))
            elif len(order_result) > 0 and order_result[0]["status"] =="unfilled" and order_result[0]["price"] == str(item["desired_value"]):
                if int(item["desired_value"]) > self.last_val*1.15:
                    self.order_cancel_transaction(machine=self.machine, db_handler=self.db_handler, currency_type=self.currency_type, item=item)
                    self.update_trade_status(db_handler=self.db_handler,
                                             item_id={"_id":item["_id"]},
                                             value={"status":"KEEP_ORDERED"})
                    #self.pusher.send_message("#push", "keeped:"+str(item))

    def check_sell_completed(self):
        sell_completed = self.db_handler.find_items({"currency":self.currency_type, "$or":[{"status":"SELL_COMPLETED"},{"status":"CANCEL_ORDERED"}]}, "trader", "trade_status")
        for item in sell_completed:
            self.db_handler.insert_item(item, "trader", "trade_history")
            self.db_handler.delete_items({"_id":item["_id"]}, "trader", "trade_status")

    def check_keep_ordered(self):
        keeped_orders = self.db_handler.find_items({"currency":self.currency_type, "status":"KEEP_ORDERED"}, "trader", "trade_status")
        for item in keeped_orders:
            if int(item["desired_value"])*0.9 < self.last_val:
                self.order_sell_transaction(machine=self.machine, db_handler=self.db_handler, currency_type=self.currency_type, item=item)
                #self.pusher.send_message("#push", "keep_sell_ordered:"+str(item))
                logger.info("sell order from keeped"+str(item["_id"]))
 
    def check_my_order(self):
        self.check_buy_ordered()
        self.check_buy_completed()
        self.check_sell_ordered()
        self.check_sell_completed()
        self.check_keep_ordered()

    def run(self):
        if self.params["is_active"]=="active":
            self.check_my_order()
            self.scenario()
        else:
            logger.info("inactive")

if __name__ == "__main__":
    mongodb = MongoDBHandler(mode="local", db_name="coiner", collection_name="price_info")
    korbit_machine = KorbitMachine()
    pusher = PushSlack()
    
    if len(sys.argv) > 0:
        trader = StepTrade(machine=korbit_machine, db_handler=mongodb, strategy=sys.argv[1], currency_type=sys.argv[2], pusher=pusher)
        trader.run()
    
