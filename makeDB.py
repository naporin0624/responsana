import os
import re
from abc import ABCMeta, abstractmethod
from urllib.parse import urljoin, urlparse

from flask_restful import Resource, reqparse
from lxml.html import *
from pymongo import MongoClient
from requests import get


class voiceScraping(metaclass=ABCMeta):
    def __init__(self, url):
        html = get(url).content.decode()
        #u付き文字を削除
        html = self.__removeStr(html)
        #ページごとにいらないタグ等を削除
        html = self.easyHandleHTML(html)

        #カテゴリーを抽出
        self.category = self.getCategory(html)
        #mp3urlリストを抽出
        self.mp3_url_list = self.getURLList(html)
        #mp3nameリストを抽出
        self.mp3_name_list = self.getNameList(html)

    #いらないタグを削除するメソッド
    def easyHandleHTML(self, html):
        return html

    #配信タイトルとかボタンカテゴリを取得するメソッド
    @abstractmethod
    def getCategory(self, html):
        pass

    #ボタンのurlを抜き出すメソッド
    @abstractmethod
    def getURLList(self, html):
        pass

    #ボタンの名前を抜き出すメソッド
    @abstractmethod
    def getNameList(self, html):
        pass

    #u付き文字を削除するメソッド
    def __removeStr(self, x):
        re_sub = re.compile(r'\\u[0-9]+')
        return re.sub(re_sub, '', x)

    #得たデータをカテゴリごとにまとめて返すメソッド
    def getData(self):
        return list(map(lambda x:{"category":x[0], "contents":x[1], "names":x[2]}, zip(self.category, self.mp3_url_list, self.mp3_name_list)))


class sanaScraping(voiceScraping):
    re_pattern = re.compile(r"<b>.*?</b>")

    def easyHandleHTML(self, html):
        start = html.index('<hr style="margin: 1em 0 ;">')
        end = html.index('<footer>')
        return html[start:end]

    def getCategory(self, html):
        category_list = re.findall(self.re_pattern, html)
        return list(map(lambda x: x.strip("<b>").strip("</b>"), category_list))

    def getURLList(self, html):
        url_list = re.split(self.re_pattern, html)
        return list(map(self.__pickMp3, url_list))[1:]

    def getNameList(self, html):
        button_list = re.split(self.re_pattern, html)
        # mp3_url_list = list(map(self.__pickMp3, url_list))[1:]
        mp3_name_list = list(map(self.__pickName, button_list))
        return mp3_name_list[1:]

    def __pickMp3(self, x):
        dl_url = "https://www.natorisana.love/sounds/"
        html = fromstring(x)
        mp3_list = html.xpath("//button/@data-file")
        mp3_list = list(map(lambda x: dl_url + x + ".mp3", mp3_list))
        return mp3_list

    def __pickName(self, x):
        html = fromstring(x)
        name_list = html.xpath("//button/text()")
        # name_list = list(map(lambda x: x.xpath("//button/text"), x))
        # name_list = list(map(lambda x: x.split("/")[-1].strip(".mp3"), x))
        return name_list


class onyankoScraping(voiceScraping):
    def easyHandleHTML(self, html):
        pass

    def getCategory(self, html):
        pass

    def getURLList(self, html):
        pass

    def getMP3List(self, html):
        pass


# class sanaScraping:
#     def __init__(self):
#         html = get("https://www.natorisana.love").content.decode()
#         html = self.__removeStr(html)
#         # important-notifyまでいらないので削除
#         html = html[html.index('<hr style="margin: 1em 0 ;">'):html.
#                     index('<footer>')]

#         re_pattern = re.compile(r"<b>.*?</b>")

#         self.category = list(
#             map(lambda x: x.strip("<b>").strip("</b>"),
#                 re.findall(re_pattern, html)))
#         self.mp3_url_list = list(
#             map(self.__pickMp3, re.split(re_pattern, html)))[1:]
#         self.mp3_name_list = list(map(self.__pickName, self.mp3_url_list))

#     def getData(self):
#         return list(map(lambda x:{"category":x[0], "contents":x[1], "names":x[2]}, zip(self.category, self.mp3_url_list, self.mp3_name_list)))

#     def __removeStr(self, x):
#         re_sub = re.compile(r'\\u[0-9]+')
#         return re.sub(re_sub, '', x)

#     def __pickMp3(self, x):
#         html = fromstring(x)
#         mp3_list = html.xpath("//button/@data-file")
#         mp3_list = list(
#             map(lambda x: "https://www.natorisana.love/sounds/" + x + ".mp3",
#                 mp3_list))
#         return mp3_list

#     def __pickName(self, x):
#         name_list = list(map(lambda x: x.split("/")[-1].strip(".mp3"), x))
#         return name_list

if __name__ == "__main__":
    MONGO_URL = 'mongodb://heroku_6vdmtkbn:ng692uvshhevmr483e7v2ua0b1@ds135724.mlab.com:35724/heroku_6vdmtkbn'
    sanaButtonURL = "https://www.natorisana.love"
    onyankoButtonURL = ""

    client = MongoClient(MONGO_URL)
    db = client[urlparse(MONGO_URL).path[1:]]
    sana = db.responsana
    onyanko = db.responyanko

    for data in sanaScraping(sanaButtonURL).getData():
        selectJson = {"category": data["category"]}
        setJson = {
            "category": data["category"],
            "contents": data["contents"],
            "names": data["names"]
        }
        sana.update(selectJson, setJson, upsert=True)

    # for data in onyankoScraping(onyankoButtonURL).getData():
    #     selectJson = {"category": data["category"]}
    #     setJson = {
    #         "category": data["category"],
    #         "contents": data["contents"],
    #         "names": data["names"]
    #     }
    #     onyanko.updata(selectJson, setJson, upsert=True)
