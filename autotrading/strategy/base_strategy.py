from abc import ABC, abstractmethod
import datetime
from autotrading.logger import get_logger

logger = get_logger("base_strategy")

class Strategy(ABC):
    @abstractmethod
    def run(self):
        pass

    def update_trade_status(self, db_handler=None, item_id=None, value=None):
        """트레이드 현재 상태를 update하기 위한 메소드
        
        Args:
             db_handler(obj): 대상 DB의 모듈 객체
             item_id(dict): 업데이트 조건 
             value(dict): 업데이트 하려는 문서의 컬럼과 값
        """
        if db_handler is None or item_id is None or value is None:
            raise Exception("Need to buy value or status")
        db_handler.set_db_collection("trader","trade_status")
        db_handler.update_items(item_id, {"$set":value})

    def order_buy_transaction(self, machine=None, db_handler=None, currency_type=None, item=None, order_type="limit"):
        """매수 주문과 함께 DB에 필요한 데이터를 입력 작업을 위한 메소드 
        Args:
            machine(obj): 매수 주문하려는 거래소 모듈 객체
            db_handler(obj): 매수 주문정보를 입력하려는 DB 모듈 객체
            currency_type(str): 매수 주문하려는 화폐 종류 
            item(dict): 매수 완료후 DB에 저장하려는 데이터
            order_type(str): 매수 방법
            
        Returns:
            OrderId(str):매수 완료 후 주문 id 
        """
        if currency_type is None or item is None:
            raise Exception("Need to param")
        db_handler.set_db_collection("trader","trade_status")
        result = machine.buy_order(currency_type=currency_type,
                                    price=str(item["buy"]),
                                    qty=str(item["buy_amount"]),#str(self.BUY_COUNT),
                                    order_type=order_type)
        if result["status"] == "success":
            db_handler.insert_item({"status":"BUY_ORDERED",
                                    "currency":currency_type,
                                    "buy_order_id":str(result["orderId"]),
                                    "buy_amount":float(item["buy_amount"]),
                                    "buy":int(item["buy"]),
                                    "buy_order_time":int(datetime.datetime.now().timestamp()),
                                    "desired_value":int(item["desired_value"]),
                                    "transaction_status":"success",
                                    "machine":str(machine)})
            return result["orderId"]
        else:
            logger.info(result)
            logger.info(item)
            db_handler.update_items({"_id":item["_id"]},{"error": "failed"})
            return None

    def order_sell_transaction(self, machine=None, db_handler=None, currency_type=None, item=None, order_type="limit"):
        """매도 주문과 함께 DB에 필요한 데이터 업데이트 작업을 위한 메소드 
        Args:
            machine(obj): 매도 주문하려는 거래소 모듈 객체
            db_handler(obj): 매도 주문정보를 입력하려는 DB 모듈 객체
            currency_type(str): 매도 주문하려는 화폐 종류 
            item(dict): 매도 완료후 DB에 저장하려는 데이터
            order_type(str): 매도 방법
            
        Returns:
            OrderId(str):매수 완료 후 주문 id 
        """
        if currency_type is None or item is None:
            raise Exception("Need to param")
        db_handler.set_db_collection("trader","trade_status")
        result = machine.sell_order(currency_type=currency_type,
                                        price=str(item["desired_value"]),
                                        qty=str(round(item["real_buy_amount"],8)),
                                        order_type=order_type)
        if result["status"] == "success":
            db_handler.update_items({"_id":item["_id"]},
                        {"$set":{"status":"SELL_ORDERED",
                        "desired_value":int(item["desired_value"]),
                        "sell_order_id":str(result["orderId"]),
                        "error":"success"}
                        })
            return result["orderId"]
        else:
            logger.info(result)
            logger.info(item)
            db_handler.update_items({"_id":item["_id"]},{"error": "failed"})
            return None

    def order_cancel_transaction(self, machine=None, db_handler=None, currency_type=None, item=None):
        """취소 주문과 함께 DB에 필요한 데이터를 업데이트 작업을 위한 메소드 
        Args:
            machine(obj): 취소 주문하려는 거래소 모듈 객체
            db_handler(obj): 취소 주문정보를 하려는 DB 모듈 객체
            currency_type(str): 취소 주문하려는 화폐 종류 
            item(dict): 취소 주문에 필요한 데이터
            order_type(str): 매수 방법
            
        Returns:
            OrderId(str):매수 완료 후 주문 id 
        """
        db_handler.set_db_collection("trader","trade_status")
        if currency_type is None or item is None:
            raise Exception("Need to param")
        if item["status"] == "BUY_ORDERED":
            result = machine.cancel_order(currency_type=currency_type, order_id=item["buy_order_id"])
            if result[0]["status"] == "success":
                db_handler.update_items({"_id":item["_id"]}, {"$set":{"status":"CANCEL_ORDERED", "cancel_order_time":int(datetime.datetime.now().timestamp()),
                                "error":"success"}})
                return item["buy_order_id"] 
            else:
                logger.info(result)
                logger.info(item)
                return None
        elif item["status"] == "SELL_ORDERED":
            result = machine.cancel_order(currency_type=currency_type, order_id=item["sell_order_id"])
            if result[0]["status"] == "success":
                db_handler.update_items({"_id":item["_id"]}, {"$set":{"status":"CANCEL_ORDERED", "cancel_order_time":int(datetime.datetime.now().timestamp()),
                                "error":"success"}})
                return item["sell_order_id"] 
            else:
                logger.info(result)
                logger.info(item)
                return None
