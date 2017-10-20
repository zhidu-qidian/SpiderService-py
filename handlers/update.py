# coding:utf-8
import json
from .base import BaseHandler


class UpdateBaseHandler(BaseHandler):
    name = "Update-Base-Handler"


class UpdateCommentHandler(UpdateBaseHandler):
    name = "Update-Comment-Handler"

    def put(self):
        """
        根据docid或者nid更新某篇文章的评论数（文章表示任意已入库的图文音视频资讯）
        :return:
        """
        docid = self.get_argument("docid", "").strip()
        num = self.get_argument("n", "").strip()
        if not docid or not num:
            self.send_error(status_code=500, reason="params illegal or not exist")
        try:
            num = int(num)
        except Exception:
            self.send_error(status_code=500, reason="can't convert param-n to int type")
        result = self.update_comment_num(docid, num)
        if isinstance(result, Exception):
            self.send_error(status_code=500, reason=str(result))
        else:
            self.write({"message": "success"})

    def update_comment_num(self, docid, num):
        sql = "UPDATE newslist_v2 SET comment=comment+%s WHERE docid='%s' RETURNING title;" % (num, docid)
        result = self.exec_sql(sql)
        return result
