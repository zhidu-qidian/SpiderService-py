# coding:utf-8
import os
from tornado.web import StaticFileHandler

doc_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../api_doc/site"))
routers = [
    (r'(.*?)', StaticFileHandler, {"path": doc_path, "default_filename": "index.html"}),
]
