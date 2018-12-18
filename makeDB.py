from requests import get
from lxml.html import *
from urllib.parse import urljoin, urlparse
import os
from flask_restful import Resource, reqparse
from pymongo import MongoClient
import re


class sanaScraping:
    def __init__(self):
        html = get("https://www.natorisana.love").content.decode()
        html = self.__removeStr(html)
        # important-notifyまでいらないので削除
        html = html[html.index('<hr style="margin: 1em 0 ;">'):html.
                    index('<footer>')]

        re_pattern = re.compile(r"<b>.*?</b>")

        self.category = list(
            map(lambda x: x.strip("<b>").strip("</b>"),
                re.findall(re_pattern, html)))
        self.mp3_url_list = list(
            map(self.__pickMp3, re.split(re_pattern, html)))[1:]
        self.mp3_name_list = list(map(self.__pickName, self.mp3_url_list))

    def getData(self):
        return list(map(lambda x:{"category":x[0], "contents":x[1], "names":x[2]}, zip(self.category, self.mp3_url_list, self.mp3_name_list)))

    def __removeStr(self, x):
        re_sub = re.compile(r'\\u[0-9]+')
        return re.sub(re_sub, '', x)

    def __pickMp3(self, x):
        html = fromstring(x)
        mp3_list = html.xpath("//button/@data-file")
        mp3_list = list(
            map(lambda x: "https://www.natorisana.love/sounds/" + x + ".mp3",
                mp3_list))
        return mp3_list

    def __pickName(self, x):
        name_list = list(map(lambda x: x.split("/")[-1].strip(".mp3"), x))
        return name_list


if __name__ == "__main__":
    MONGO_URL = 'mongodb://heroku_6vdmtkbn:ng692uvshhevmr483e7v2ua0b1@ds135724.mlab.com:35724/heroku_6vdmtkbn'
    client = MongoClient(MONGO_URL)
    db = client[urlparse(MONGO_URL).path[1:]]
    co = db.responsana
    for data in sanaScraping().getData():
        co.update({
            "category": data["category"]
        }, {
            "category": data["category"],
            "contents": data["contents"],
            "names": data["names"]
        },
                  upsert=True)
