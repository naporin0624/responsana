import os
import re
from abc import ABCMeta, abstractmethod
from urllib.parse import urljoin, urlparse

from flask_restful import Resource, reqparse
from lxml.html import *
from pymongo import MongoClient
from requests import get
if os.path.isfile("mongokey.py"): from mongokey import MONGO_URL
else: MONGO_URL = os.environ["MONGO_URL"]


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
        re_sub = re.compile(r'u[0-9]+')
        result = re.sub(re_sub, '', x).replace("\\", "")
        return result

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
        return name_list


class onyankoScraping(voiceScraping):
    re_pattern = re.compile(r"<text>.*?</text>")

    def easyHandleHTML(self, html):
        start = html.index("<text>【Minecraft】バビニクラフト #6(12/17追加)</text></br>")
        end = html.index("まだテスト中じゃよ。。。")
        return html[start:end]

    def getCategory(self, html):
        category_list = re.findall(self.re_pattern, html)
        return list(
            map(lambda x: x.strip("<text>").strip("</text>"), category_list))

    def getURLList(self, html):
        url_list = re.split(self.re_pattern, html)[1:]
        return list(map(self.__pickMp3, url_list))

    def getNameList(self, html):
        button_list = re.split(self.re_pattern, html)[1:]
        mp3_name_list = list(map(self.__pickName, button_list))
        return mp3_name_list

    def __pickMp3(self, x):
        dl_url = "http://onyankopbtn.html.xdomain.jp/sound/"
        html = fromstring(x)
        mp3_list = html.xpath("//input/@data-file")
        mp3_list = list(map(lambda x: dl_url + x + ".mp3", mp3_list))
        return mp3_list

    def __pickName(self, x):
        html = fromstring(x)
        name_list = html.xpath("//input/@value")
        return name_list


if __name__ == "__main__":
    sanaButtonURL = "https://www.natorisana.love"
    onyankoButtonURL = "http://onyankopbtn.html.xdomain.jp"

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

    for data in onyankoScraping(onyankoButtonURL).getData():
        selectJson = {"category": data["category"]}
        setJson = {
            "category": data["category"],
            "contents": data["contents"],
            "names": data["names"]
        }
        onyanko.update(selectJson, setJson, upsert=True)
