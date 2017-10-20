# coding:utf-8
import json
from .base import BaseHandler
from models.models import *
from models.errors import *
from utils.alioss import upload_img, delete_img
from utils.general import format_insert_sql
from utils.general import get_default_time


class StoreBaseHandler(BaseHandler):
    name = "Store-Base-Handler"

    def adapt_params(self, params):
        pass

    def get_json_params(self):
        try:
            param = self.request.body.decode('utf-8')
            param_json = json.loads(param)
        except Exception as e:
            param_json = e
        return param_json

    def prepare_publish_name(self, name, url, refer):
        """
        查找或添加pname并返回
        :param url:
        :param refer:
        :return: pname
        """
        pname = PublishName()
        pname.name = name
        pname_selected = self.select_pname(pname)
        _icon = ""
        if isinstance(pname_selected, Exception):
            return pname_selected
        if len(url) > 10:
            _icon = upload_img(url, refer)
            if isinstance(_icon, Exception):
                print str(_icon)
            else:
                pname.icon = _icon
        pname_store_result = self.store_pname(pname)
        if isinstance(pname_store_result, Exception) and len(str(_icon)) > 10:
            _icon = _icon.split("/")[-1]
            icon_delete_result = delete_img(_icon)
            if isinstance(icon_delete_result, Exception):
                print str(icon_delete_result)
        return pname

    def store_pname(self, pname):
        sql = "INSERT INTO newspublisherlist_v2 (ctime, name, icon) VALUES ($1, $2, $3)RETURNING id"
        sql_exe_result = self.exec_sql(sql)
        if not isinstance(sql_exe_result, Exception):
            pname.id = sql_exe_result[0][0]
        return pname

    def select_source(self, source):
        sql = "SELECT id, cid, scid, sname, state FROM sourcelist_v2 WHERE id=%s" % source.id
        sql_exe_result = self.exec_sql(sql)
        if not isinstance(sql_exe_result, Exception):
            if not sql_exe_result:
                return NoSuchObjectError()
            else:
                source.id = sql_exe_result[0][0]
                source.channel_id = sql_exe_result[0][1]
                source.second_channel_id = sql_exe_result[0][2]
                source.name = sql_exe_result[0][3]
                source.state = sql_exe_result[0][4]
        return source

    def select_pname(self, pname):
        sql = "SELECT id, ctime, name, icon FROM newspublisherlist_v2 WHERE name='%s'" % pname.name
        sql_exe_result = self.exec_sql(sql)
        if isinstance(sql_exe_result, Exception):
            return sql_exe_result
        if not sql_exe_result:
            return NoSuchObjectError("No Such Pname: %s" % pname.name)
        pname.id = sql_exe_result[0][0]
        pname.insert_time = sql_exe_result[0][1]
        pname.name = sql_exe_result[0][2]
        pname.icon = sql_exe_result[0][3]
        return pname

    def set_default_headers(self):
        self.set_header('Access-Control-Allow-Origin', '*')
        self.set_header('Access-Control-Allow-Methods', 'POST, GET, OPTIONS')
        self.set_header('Access-Control-Max-Age', 1000)
        self.set_header('Access-Control-Allow-Headers', '*')
        self.set_header('Content-type', 'application/json')

    def delete_news(self, news):
        sql = "delete from newslist_v2 where nid ='%s' ;" % news.nid
        sql_exe_result = self.exec_sql(sql)
        return sql_exe_result

    def store_news(self, news):
        table = "newslist_v2"
        fields = ["url", "docid", "title", "author", "ptime", "pname", "purl",
                  "tags", "province", "city", "district", "comment", "inum", "style", "imgs", "state", "ctime", "chid",
                  "sechid", "srid", "icon", "videourl", "thumbnail", "duration", "rtype", "concern", "un_concern",
                  "clicktimes", "srstate", "sec_purl_id"]
        returns = ["nid"]
        sql = format_insert_sql(table, fields, returns)
        sechid = None
        if news.second_channel_id != 0:
            sechid = news.second_channel_id
        sql_exe_result = self.exec_sql(sql)
        if not isinstance(sql_exe_result, Exception):
            news.nid = sql_exe_result[0][0]
            return news
        else:
            return sql_exe_result


class StoreNewsHandler(StoreBaseHandler):
    """
    新闻存储处理
    """
    name = "Store-News-Handler"

    def post(self):
        """
        存储新闻并处理其中pname的icon
        :return:
        """
        params = self.get_json_params()
        news = self.adapt_to_news(params)
        if isinstance(news, Exception):
            self.send_error(status_code=500, reason=str(news))
        pname = self.prepare_publish_name(news.publish_name,
                                          params.get("site_icon", ""),
                                          news.publish_url)
        if isinstance(pname, Exception):
            self.send_error(status_code=500, reason=str(pname))
        news.icon = pname.icon
        news_store_result = self.store_news(news)
        if isinstance(news_store_result, Exception):
            self.send_error(status_code=500, reason=str(news_store_result))
        nnews = self.adapt_to_nnews(params, news.nid)
        if isinstance(nnews, Exception):
            self.send_error(status_code=500, reason=str(nnews))
        nnews.icon = pname.icon
        nnews.channel_id = news.channel_id
        nnews.second_channel_id = news.second_channel_id
        nnews.style = news.style
        nnews_store_result = self.store_nnews(nnews)
        if isinstance(nnews_store_result, Exception):
            news_delete_result = self.delete_news(news)
            if isinstance(news_delete_result, Exception):
                print str(news_delete_result)
            self.send_error(status_code=500, reason=str(news_delete_result))
        self.write({"id": news.nid})

    def adapt_to_news(self, params):
        news = News()
        style = 0
        imgs_num = len(params.get("images", []))
        if 1 == imgs_num or 2 == imgs_num:
            style = OneStyle
        elif 3 == imgs_num:
            style = ThreeStyle
        else:
            style = ZeroStyle
        offline = 1
        if params.get("online"):
            offline = 0
        source = Source()
        source.id = params.get("source_id", 0)
        source.channel_id = params.get("channel_id", 0)
        source.second_channel_id = params.get("second_channel_id", 0)
        if 0 == source.channel_id:
            select_result = self.select_source(source)
            if isinstance(select_result, Exception):
                offline = 1
            else:
                source = select_result
        news.url = params.get("publish_url", "")
        news.unique_id = params.get("unique_id", "")
        news.title = params.get("title", "")
        news.content = params.get("content", "[]")
        news.author = params.get("author", "")
        news.publish_time = params.get("publish_time", get_default_time())
        news.publish_name = params.get("publish_site", "")
        news.publish_url = params.get("publish_url", "")
        news.tags = params.get("tags", [])
        news.province = params.get("province", "")
        news.city = params.get("city", "")
        news.district = params.get("district")
        news.image_number = params.get("image_num", 0)
        news.style = style
        news.images = params.get("images", [])
        news.insert_time = params.get("insert_time", get_default_time())
        news.channel_id = int(source.channel_id)
        news.second_channel_id = int(source.second_channel_id)
        news.source_id = int(source.id)
        news.source_state = 1
        news.icon = params.get("site_icon", "")
        news.offline = offline
        news.concern = params.get("like", 0)
        news.unconcern = params.get("dislike", 0)
        news.click_times = params.get("read", 0)
        news.spider_source_id = params.get("spider_source_id", 0)

        return news

    def adapt_to_nnews(self, params, nid):
        nnews = NNews()
        nnews.nid = nid
        nnews.url = params.get("publish_url", "")
        nnews.unique_id = params.get("unique_id", "")
        nnews.title = params.get("title", "")
        nnews.content = params.get("content")
        nnews.author = params.get("author", "")
        nnews.publish_time = params.get("publish_time", get_default_time())
        nnews.publish_name = params.get("publish_site", "")
        nnews.publish_url = params.get("publish_url", "")
        nnews.tags = params.get("tags", [])
        nnews.province = params.get("province", "")
        nnews.city = params.get("city", "")
        nnews.district = params.get("district", "")
        nnews.image_number = params.get("image_numer", 0)
        nnews.images = params.get("images", [])
        nnews.insert_time = params.get("insert_time", get_default_time())
        nnews.source_id = params.get("source_id", 0)

        return nnews

    def store_nnews(self, nnews):
        table = "info_news"
        fields = ["nid", "url", "docid", "title", "content", "author", "ptime", "pname", "purl", "tags",
                  "province", "city", "district", "inum", "style", "imgs", "ctime", "chid", "sechid", "srid", "icon"]
        returns = ["nid"]
        sql = format_insert_sql(table, fields, returns)
        sechid = None
        if nnews.second_channel_id != 0:
            sechid = nnews.second_channel_id

        params = [nnews.nid, nnews.url, nnews.unique_id, nnews.title, nnews.content, nnews.author,
                  nnews.publish_time, nnews.publish_name, nnews.publish_url,
                  nnews.tags, nnews.province, nnews.city, nnews.district, nnews.image_number,
                  nnews.style, nnews.images, nnews.insert_time, nnews.channel_id, sechid, nnews.source_id, nnews.icon]
        sql_exe_result = self.exec_sql(sql, params)
        return sql_exe_result


class StoreJokeHandler(StoreBaseHandler):
    """
    段子存储处理
    """
    name = "Store-Joke-Handler"

    def post(self):
        """
        存储段子并处理其中pname的icon
        :return:
        """
        params = self.get_json_params()
        news = self.adapt_to_news(params)
        if isinstance(news, Exception):
            self.send_error(status_code=500, reason=str(news))
        pname = self.prepare_publish_name(news.publish_name,
                                          params.get("site_icon", ""),
                                          news.publish_url)
        if isinstance(pname, Exception):
            self.send_error(status_code=500, reason=str(pname))
        news.icon = pname.icon
        news_store_result = self.store_news(news)
        if isinstance(news_store_result, Exception):
            self.send_error(status_code=500, reason=str(news_store_result))
        joke = self.adapt_to_joke(params, news.nid)
        if isinstance(joke, Exception):
            self.send_error(status_code=500, reason=str(joke))
        joke.icon = pname.icon
        joke_store_result = self.store_joke(joke)
        if isinstance(joke_store_result, Exception):
            # 段子存储失败，新闻也要删掉
            news_delete_result = self.delete_news(news)
            if isinstance(news_delete_result, Exception):
                print str(news_delete_result)
            self.send_error(status_code=500, reason=str(joke_store_result))
        self.write({"id": news.nid})

    def adapt_to_news(self, params):
        news = News()
        offline = 1
        if params.get("online"):
            offline = 0
        news.url = params.get("unique_id", "")
        news.unique_id = params.get("unique_id", "")
        news.title = params.get("title", "")
        news.author = params.get("author", "")
        news.publish_time = params.get("publish_time", get_default_time())
        news.publish_name = params.get("publish_site", "")
        news.style = params.get("style", ThreeStyle)
        news.offline = offline
        news.insert_time = params.get("insert_time", get_default_time())
        news.channel_id = JokeChannel
        news.source_id = params.get("source_id", 0)
        news.source_state = 0
        news.icon = params.get("site_icon", "")
        news.return_type = JokeType
        news.content = "[]"
        news.concern = params.get("like", 0)
        news.unconcern = params.get("dislike", 0)
        news.image_number = params.get("image_number", 0)
        news.images = params.get("images", [])
        news.spider_source_id = params.get("spider_source_id", "")

        return news

    def adapt_to_joke(self, params, nid):

        joke = Joke()

        joke.nid = nid
        joke.unique_id = params.get("unique_id", "")
        joke.content = params.get("content", "")
        joke.author = params.get("author", "")
        joke.avatar = params.get("author_icon", "")
        joke.publish_time = params.get("publish_time", get_default_time())
        joke.publish_name = params.get("publish_site", "")
        joke.style = params.get("style", ThreeStyle)
        joke.insert_time = params.get("insert_time")
        joke.channel_id = JokeChannel
        joke.source_id = params.get("source_id", 0)
        joke.icon = params.get("site_icon", "")
        joke.images = params.get("images", [])

        return joke

    def store_joke(self, joke):
        table = "info_joke"
        fields = ["nid", "docid", "content", "author", "avatar", "ptime", "pname",
                  "style", "imgs", "ctime", "chid", "srid", "icon"]
        returns = ["nid"]
        params = [joke.nid, joke.unique_id, joke.content, joke.author, joke.avatar, joke.publish_time,
                  joke.publish_name, joke.style, joke.images, joke.insert_time, joke.channel_id,
                  joke.source_id, joke.icon]
        sql = format_insert_sql(table, fields, returns)
        sql_exe_result = self.exec_sql(sql, params)
        if isinstance(sql_exe_result, Exception):
            return sql_exe_result
        else:
            joke.nid = sql_exe_result[0][0]
            return joke


class StoreVideoHandler(StoreBaseHandler):
    """
    视频存储处理
    """
    name = "Store-Video-Handler"

    def post(self):
        """
        存储视频并处理其中pname的icon
        :return:
        """
        params = self.get_json_params()

        news = self.adapt_to_news(params)
        if isinstance(news, Exception):
            self.send_error(status_code=500, reason=str(news))
        pname = self.prepare_publish_name(news.publish_name,
                                          params.get("site_icon", ""),
                                          news.publish_url)

        if isinstance(pname, Exception):
            self.send_error(status_code=500, reason=str(pname))
        news.icon = pname.icon
        news_store_result = self.store_news(news)
        if isinstance(news_store_result, Exception):
            self.send_error(status_code=500, reason=str(news_store_result))
        video = self.adapt_to_video(params, news.nid)
        if isinstance(video, Exception):
            self.send_error(status_code=500, reason=str(pname))
        video.icon = pname.icon
        video_store_result = self.store_video(video)
        if isinstance(video_store_result, Exception):
            news_delete_result = self.delete_news(news)
            if isinstance(news_delete_result, Exception):
                print str(news_delete_result)
            self.send_error(status_code=500, reason=str(video_store_result))
        self.write({"id": news.nid})

    def adapt_to_news(self, params):
        news = News()
        offline = 1
        if params.get("online"):
            offline = 0
        news.url = params.get("publish_url", "")
        news.unique_id = params.get("unique_id", "")
        news.title = params.get("title", "")
        news.author = params.get("author", "")
        news.publish_time = params.get("publish_time", get_default_time())
        news.publish_name = params.get("publish_site", "")
        news.publish_url = params.get("publish_url", "")
        news.style = VideoStyle
        news.offline = offline
        news.insert_time = params.get("insert_time", get_default_time())
        news.channel_id = params.get("chanel_id", 0)
        news.second_channel_id = params.get("second_channel_id", 0)
        news.source_id = params.get("source_id", 0)
        news.source_state = 0
        news.icon = params.get("site_icon")
        news.video_url = params.get("video_url", "")
        news.thumbnail = params.get("video_thumbnail", "")
        news.duration = params.get("video_duration", 0)
        news.return_type = VideoType
        news.content = "[]"
        news.click_times = params.get("play_times", 0)
        news.tags = params.get("tags", [])
        news.concern = params.get("like", 0)
        news.unconcern = params.get("dislike", 0)
        news.comment = params.get("comment", 0)
        news.spider_source_id = params.get("spider_source_id", "")

        return news

    def adapt_to_video(self, params, nid):
        video = Video()
        video.nid = nid
        video.url = params.get("publish_url", "")
        video.unique_id = params.get("unique_id", "")
        video.title = params.get("title", "")
        video.author = params.get("author", "")
        video.publish_time = params.get("publish_time", get_default_time())
        video.publish_name = params.get("publish_site", "")
        video.images = params.get("video_thumbnail", "")
        video.insert_time = params.get("insert_time", get_default_time())
        video.channel_id = params.get("channel_id", 0)
        video.source_id = params.get("source_id", 0)
        video.second_channel_id = params.get("second_channel_id", 0)
        video.icon = params.get("site_icon", "")
        video.video_url = params.get("video_url", "")
        video.duration = params.get("video_duration", 0)
        video.tags = params.get("tags", [])
        return video

    def store_video(self, video):
        table = "info_video"
        fields = ["nid", "url", "docid", "title", "author", "ptime", "pname", "style",
                  "imgs", "ctime", "chid", "srid", "sechid", "icon", "videourl", "duration",
                  "tags"]
        returns = ["nid"]
        params = [video.nid, video.url, video.unique_id, video.title, video.author, video.publish_time,
                  video.publish_name, video.style, video.images, video.insert_time, video.channel_id,
                  video.source_id, video.second_channel_id, video.icon, video.video_url, video.duration,
                  video.tags]
        sql = format_insert_sql(table, fields, returns)
        sql_exe_result = self.exec_sql(sql, params)
        if isinstance(sql_exe_result, Exception):
            return sql_exe_result
        else:
            video.nid = sql_exe_result[0][0]
            return video


class StoreCommentHnadler(StoreBaseHandler):
    """
    评论存储处理
    """
    name = "Store-Comment-Handler"

    def post(self):
        """
        存储评论
        :return:
        """
        params = self.get_json_params()
        if isinstance(params, Exception):
            self.send_error(status_code=500, reason=str(params))
        comment = self.adapt_params(params)
        if isinstance(comment, Exception):
            self.send_error(status_code=500, reason=str(comment))
        insert_id = self.store_comment(comment)
        if isinstance(insert_id, Exception):
            self.send_error(status_code=500, reason=str(insert_id))
        else:
            self.write({"id": insert_id})

    def store_comment(self, comment):
        table = "commentlist_v2"
        fields = ["content", "commend", "ctime", "uname", "avatar", "docid", "cid"]
        returns = ["id"]
        sql = format_insert_sql(table, fields, returns)
        params = [comment.content, comment.commend, comment.insert_time, comment.user_name,
                  comment.avatar, comment.foreign_id, comment.unique_id]
        result = self.exec_sql(sql, params)
        if isinstance(result, Exception):
            return result
        insert_id = result[0][0]
        return insert_id

    def adapt_params(self, params):
        comment = Comment()
        comment.content = params.get("content", "")
        comment.commend = params.get("commend", 0)
        comment.insert_time = params.get("insert_time", get_default_time())
        comment.user_name = params.get("user_name", "")
        comment.avatar = params.get("avatar", "")
        comment.foreign_id = params.get("foreign_id", "")
        comment.unique_id = params.get("unique_id", "")
        return comment
