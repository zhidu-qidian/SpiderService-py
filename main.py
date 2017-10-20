# coding:utf-8
import os
import tornado.httpserver
import tornado.ioloop
from tornado.options import define, options
from psycopg2.pool import SimpleConnectionPool
import tornado.web
import configs
import routers
from utils.gen_doc import gen_api_doc


class Application(tornado.web.Application):
    def __init__(self):
        self.urls = routers.service_routers
        self.settings = configs.SETTINGS
        super(Application, self).__init__(self.urls, **self.settings)
        self.pg = None
        self.init_db()

    def init_db(self):
        self.pg = SimpleConnectionPool(minconn=1,
                                       maxconn=self.settings["pg_maxconn"],
                                       database=self.settings["pg_db"],
                                       user=self.settings["pg_user"],
                                       password=self.settings["pg_passwd"],
                                       host=self.settings["pg_host"],
                                       port=self.settings["pg_port"])
        print "DB-Init complete"


if __name__ == "__main__":
    define("port", default=configs.SETTINGS["server_port"],
           help="run on the given port", type=int)
    define("host", default=configs.SETTINGS["server_host"],
           help="run on the given host", type=str)
    define("gen_doc", default=0, type=int)
    options.parse_command_line()

    print "Define-Pasrse complete"
    app = Application()
    if options.gen_doc != 0:
        gen_api_doc(app)
    http_server = tornado.httpserver.HTTPServer(app)
    http_server.listen(options.port, address=options.host)
    print "Start Listen...(host:%sport:%s)" % (options.host, options.port)
    tornado.ioloop.IOLoop.instance().start()
