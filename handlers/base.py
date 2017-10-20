# coding:utf-8
import json
import tornado.web


class BaseHandler(tornado.web.RequestHandler):
    """
    Handler基类
    """
    name = "Base-Handler"

    def get(self, *args, **kwargs):
        self.write(self.name)

    def post(self):
        param = self.request.body.decode('utf-8')
        param = json.loads(param)
        self.write(json.dumps(param))

    def mogrify_sql(self, sql, params=None):
        conn = self.application.pg.getconn()
        cursor = conn.cursor()
        result = None
        if not params:
            result = cursor.mogrify(sql)
        else:
            result = cursor.mogrify(sql, params)
        cursor.close()
        self.application.pg.putconn(conn)
        return result

    def exec_sql(self, sql, params=None):
        conn = self.application.pg.getconn()
        cursor = conn.cursor()
        try:
            if not params:
                cursor.execute(sql)
            else:
                cursor.execute(sql, params)
            result = cursor.fetchall()
        except Exception as e:
            result = e
        else:
            conn.commit()
            cursor.close()
        finally:
            self.application.pg.putconn(conn)
        return result
