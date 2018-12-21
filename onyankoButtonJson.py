from requests import get
from lxml.html import *
from urllib.parse import urljoin, urlparse
import os
from flask_restful import Resource, reqparse
# from pydub import AudioSegment
from pymongo import MongoClient
MONGO_URL = os.environ["MONGO_URL"]
client = MongoClient(MONGO_URL)
db = client[urlparse(MONGO_URL).path[1:]]
co = db.responyanko


class getCategory1(Resource):
    def get(self):
        # print("start get category")
        res = {"categorylist": sorted([obj["category"] for obj in co.find()])}
        return res


class getContentsNames1(Resource):
    parser = reqparse.RequestParser(bundle_errors=True)
    parser.add_argument("category", required=True)

    def get(self):
        # print("start get contents")
        args = self.parser.parse_args()
        # print("category:", args["category"])
        name_list = [
            obj["names"] for obj in co.find({
                "category": args["category"]
            })
        ][0]
        name_list.sort()
        # data = list(map(self.__makeDict, urllist))
        res = {"voicelist": name_list}
        return res


class getContentsURL1(Resource):
    parser = reqparse.RequestParser(bundle_errors=True)
    parser.add_argument("category", required=True)
    parser.add_argument("name", required=True)

    def get(self):
        args = self.parser.parse_args()
        record = [x for x in co.find({"category": args["category"]})][0]
        idx = record["names"].index(args["name"])
        url = record["contents"][idx]
        res = {"voiceurl": url}
        return res


if __name__ == "__main__":
    from urllib.parse import urljoin, urlparse
    from pymongo import MongoClient
    import os
    MONGO_URL = os.environ["MONGO_URL"]
    client = MongoClient(MONGO_URL)
    db = client[urlparse(MONGO_URL).path[1:]]
    co = db.responsana
    record = [x for x in co.find({"category": "ぽんぽこ24 リターンズ（神対応 名取さな）"})][0]
    idx = record["names"].index('まな板！？')
    url = record["contents"][idx]
    print(url)