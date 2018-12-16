from requests import get
from lxml.html import *
from urllib.parse import urljoin, urlparse
import os
from flask_restful import Resource, reqparse
from pymongo import MongoClient
from pydub import AudioSegment



# MONGO_URL = os.environ.get('MONGOHQ_URL')

class getCategory(Resource):
    parser = reqparse.RequestParser(bundle_errors=True)
    parser.add_argument("html")

    def get(self):
        pass


class getContents(Resource):
    parser = reqparse.RequestParser(bundle_errors=True)
    parser.add_argument("category")

    def get(self):
        pass

class postDataBase(Resource):
    def post(self):
        data = sanaScraping()





