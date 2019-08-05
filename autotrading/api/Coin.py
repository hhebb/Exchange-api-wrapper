"""
Coin class
"""
import json
from autotrading.db.mongodb.mongodb_handler import MongoDbHandler
from flask import jsonify, request, make_response
from flask_restful import Resource, reqparse
from bson import json_util
import datetime
import pymongo

class Coin(Resource):
    """
    Stock class
    """
    def get(self, coin_type):
        """
        Get Method
        param coin_type 
        """
        parser = reqparse.RequestParser()
        parser.add_argument('from')
        parser.add_argument('to')
        parser.add_argument('span')
        args = parser.parse_args()
        from_time = args['from']
        to_time = args['to']
        print(args)
        if args["span"] is not None:
            if args["span"] == "month":
                group_key = {"coin":"$coin", "year":"$year", "month":"$month"}
            elif args["span"] == "day":
                group_key = {"coin":"$coin", "year":"$year", "month":"$month", "day":"$day"}
            elif args["span"] == "hour":
                group_key = {"coin":"$coin", "year":"$year", "month":"$month", "day":"$day", "hour":"$hour"}
            elif args["span"] == "minute":
                group_key = {"coin":"$coin", "year":"$year", "month":"$month", "day":"$day", "hour":"$hour", "minute":"$minute"}

        else:
            group_key = {"coin":"$coin"}
        print(group_key)

        db_handler = MongoDbHandler("remote", "coiner", "price_info")
        
        now = datetime.datetime.now()
        then = now - datetime.timedelta(days=1)
        then_timestamp = int(then.timestamp())

        if from_time is not None:
            from_timestamp = int(from_time)
        else:
            resp = jsonify({"status:Need to from parameter"})
            return make_response(resp, 400)

        if to_time is not None:
            to_timestamp = int(to_time)
        else:
            to_timestamp = int(now.timestamp())

        print(from_timestamp)
        print(to_timestamp)

        result_list = []
        if args["span"] is not None:
            pipeline = [{"$match": {"$and":[{"timestamp":{"$gt":from_timestamp, "$lt":to_timestamp}}, {"coin":coin_type}]}},
                        {"$group": {"_id":group_key,
                                    "min_val":{"$min":"$price"},
                                    "max_val":{"$max":"$price"}
                                    }},
                        {"$sort":{"_id":1}}]
            """
            get a min max value
            """
            query_result = db_handler.aggregate(pipeline)
            for item in query_result:
                result_list.append(item)
        else:
            query_result = db_handler.find_item({"coin":coin_type,
                                        "timestamp":{"$gt":from_timestamp,
                                                     "$lt":to_timestamp}}).sort("timestamp", pymongo.DESCENDING)
            for item in query_result:
                item.pop("_id")
                result_list.append(item)
        resp = jsonify({"count":len(result_list), "data":result_list})
        return make_response(resp, 200)
