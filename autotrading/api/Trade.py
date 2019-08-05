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

class Trade(Resource):
    def get(self):
        parser = reqparse.RequestParser()
        parser.add_argument('status')
        args = parser.parse_args()
        db_handler = MongoDbHandler("local", "trader", "trade_status")
        if args["status"] is not None:
            query_result = db_handler.find_item({"status":args["status"]})
        else:
            query_result = db_handler.find_item({})

        result_list = []
        for item in query_result:
            item.pop("_id")
            result_list.append(item)

        resp = jsonify({"count":len(result_list), "data":result_list})
        return make_response(resp, 200)
