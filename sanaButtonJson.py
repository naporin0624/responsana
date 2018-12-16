from requests import get
from lxml.html import *
from urllib.parse import urljoin, urlparse
import os
from flask_restful import Resource, reqparse
# from pydub import AudioSegment
from pymongo import MongoClient
MONGO_URL = 'mongodb://heroku_6vdmtkbn:ng692uvshhevmr483e7v2ua0b1@ds135724.mlab.com:35724/heroku_6vdmtkbn'
client = MongoClient(MONGO_URL)
db = client[urlparse(MONGO_URL).path[1:]]
co = db.responsana


class getCategory(Resource):
    def get(self):
        print("start get category")
        res = {"categorylist": sorted([obj["category"] for obj in co.find()])}
        return res


class getContents(Resource):
    parser = reqparse.RequestParser(bundle_errors=True)
    parser.add_argument("category", required=True)

    def get(self):
        print("start get contents")
        args = self.parser.parse_args()
        print("category:", args["category"])
        urllist = [
            obj["contents"] for obj in co.find({
                "category": args["category"]
            })
        ][0]
        urllist.sort()
        data = list(map(self.__makeDict, urllist))
        res = {"voicelist": data}
        return res

    def __makeDict(self, url):
        name = url.split("/")[-1].strip(".mp3")
        print(name, url)
        return {"name": name, "url": url}