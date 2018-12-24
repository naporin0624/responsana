import json
import os
from urllib.parse import urljoin, urlparse

from flask_restful import Resource, reqparse
# from pydub import AudioSegment
from pymongo import MongoClient
from requests import get
if os.path.isfile("mongokey.py"): from mongokey import MONGO_URL
else: MONGO_URL = os.environ["MONGO_URL"]

client = MongoClient(MONGO_URL)
db = client[urlparse(MONGO_URL).path[1:]]
co = db.responsana
co_temp = db.sanatemplate


class makeTemplate(Resource):
    parser = reqparse.RequestParser(bundle_errors=True)
    parser.add_argument("template", action='append')
    parser.add_argument("name", required=True)

    def get(self):
        args = self.parser.parse_args()
        templateJson = co_temp.find_one({"name": args["name"]})
        if templateJson is None:
            res = {"retentionData": []}
        else:
            res = {'retentionData': templateJson["template"]}
        return res

    def post(self):
        args = self.parser.parse_args()
        if args["name"] not in showDataTemplate().get()["templateNameList"]:
            name = args["name"]
            template = args["template"]
            co_temp.insert({'name': name, 'template': template})
            return {"msg": "保存完了"}
        else:
            return {"msg": "もう登録されています"}

    def put(self):
        args = self.parser.parse_args()
        selectJson = {"name": args["name"]}
        setJson = {"name": args["name"], "template": args["template"]}
        co_temp.update(selectJson, setJson, upsert=True)


class showDataTemplate(Resource):
    def get(self):
        record = list(co_temp.find())
        if len(record) > 0:
            name_list = list(map(lambda x: x["name"], record))
            res = {"templateNameList": name_list}
        else:
            res = {"templateNameList": []}
        return res


class getCategory(Resource):
    def get(self):
        record = list(co.find())
        title_list = list(map(lambda x: x["category"], record))
        res = {"categoryList": sorted(title_list)}
        return res


class getContentsNames(Resource):
    parser = reqparse.RequestParser(bundle_errors=True)
    parser.add_argument("category", required=True)

    def get(self):
        args = self.parser.parse_args()
        record = list(co.find({"category": args["category"]}))[0]
        name_list = record["names"]
        name_list.sort()
        res = {"voiceList": name_list}
        return res


class getContentsURL(Resource):
    parser = reqparse.RequestParser(bundle_errors=True)
    parser.add_argument("category", required=True)
    parser.add_argument("name", required=True)

    def get(self):
        args = self.parser.parse_args()
        record = list(co.find({"category": args["category"]}))[0]
        idx = record["names"].index(args["name"])
        url = record["contents"][idx]
        res = {"voiceURL": url}
        return res


if __name__ == "__main__":
    from urllib.parse import urljoin, urlparse
    from pymongo import MongoClient
    client = MongoClient(MONGO_URL)
    db = client[urlparse(MONGO_URL).path[1:]]
    co = db.responsana

    # record = [x for x in co.find({"category": "ぽんぽこ24 リターンズ（神対応 名取さな）"})]
    # record = list(co.find({"category": "ぽんぽこ24 リターンズ（神対応 名取さな）"}))[0]
    # record = list(co_temp.find())
    # name_list = list(map(lambda x: x["names"], record))
    # print(name_list)
    # print(record)
    # print(record, len(record), len(record[0]), type(record[0]))
    # templateJson = co_temp.find_one({"name": "abcdef"})
    # test = templateJson["template"][0].replace('"', '"')
    import time
    s = time.time()
    # record = [x for x in co.find()]
    res = {"categorylist": sorted([obj["category"] for obj in co.find()])}
    print(time.time() - s)
    # record = list(record)
    # title_list = list(map(lambda x: x["category"], record))
    # res = {"categorylist": sorted(title_list)}
    # print(time.time() - s)
    # print(test)
