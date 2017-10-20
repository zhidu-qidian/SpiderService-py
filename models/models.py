# coding:utf-8

from utils.general import get_default_time


ZeroStyle = 0
OneStyle = 1
ThreeStyle = 3
VideoStyle = 6
VideoType = 6
JokeType = 8
JokeChannel = 45


class BaseModel(object):
    def to_dict(self):
        return dict(self.__dict__)

    @classmethod
    def from_dict(cls, d):
        self = cls()
        for k, v in d.items():
            self.__dict__[k] = v
        return self

    def format_insert_statement(self):
        pass


class News(BaseModel):
    def __init__(self):
        self.nid = 0
        self.url = ""
        self.unique_id = ""
        self.title = ""
        self.content = None  # json
        self.author = ""
        self.publish_time = get_default_time()
        self.publish_name = ""
        self.publish_url = ""
        self.tags = []
        self.province = ""
        self.city = ""
        self.district = ""
        self.image_number = 0
        self.style = 0
        self.images = []
        self.insert_time = get_default_time()
        self.channel_id = 0
        self.second_channel_id = 0
        self.source_id = 0
        self.icon = ""
        self.html = ""
        self.collect = 0
        self.concern = 0
        self.comment = 0
        self.offline = 0
        self.source_state = 0
        self.video_url = ""

        # self.video_type = 0
        self.thumbnail = ""
        self.duration = 0
        self.return_type = 0
        self.unconcern = 0
        self.click_times = 0

        # add for trace spider source info
        self.spider_source_id = ""

    def store(self):
        pass

    def delete(self):
        pass


class NNews(BaseModel):
    def __init__(self):
        self.nid = 0
        self.url = ""
        self.unique_id = ""
        self.title = ""
        self.content = None  # json
        self.author = ""
        self.publish_time = get_default_time()
        self.publish_name = ""
        self.publish_url = ""
        self.tags = []
        self.province = ""
        self.city = ""
        self.district = ""
        self.image_number = 0
        self.style = 0
        self.images = []
        self.insert_time = get_default_time()
        self.channel_id = 0
        self.second_channel_id = 0
        self.source_id = 0
        self.icon = ""

    def store(self):
        pass

    def delete(self):
        pass


class Video(BaseModel):
    def __init__(self):
        self.nid = 0
        self.url = ""
        self.unique_id = ""
        self.title = ""
        self.author = ""
        self.publish_time = get_default_time()
        self.publish_name = ""
        self.style = _VideoStyle
        self.images = []
        self.insert_time = get_default_time()
        self.channel_id = 0
        self.source_id = 0
        self.second_channel_id = 0
        self.icon = ""
        self.video_url = ""
        self.duration = 0
        self.tags = []

    def store(self):
        pass


class Joke(BaseModel):
    def __init__(self):
        self.nid = 0
        self.unique_id = ""
        self.content = None  # json
        self.author = ""
        self.avatar = ""
        self.publish_time = get_default_time()
        self.publish_name = ""
        self.style = JokeType
        self.images = []
        self.insert_time = get_default_time()
        self.channel_id = 0
        self.source_id = 0
        self.icon = ""

    def store(self):
        pass


class PublishName(BaseModel):
    def __init__(self):
        self.id = 0
        self.insert_time = get_default_time()
        self.name = ""
        self.icon = ""

    def store(self):
        pass

    def name_select(self):
        pass


class Comment(BaseModel):
    def __init__(self):
        self.id = 0
        self.content = ""
        self.commend = 0
        self.insert_time = get_default_time()
        self.user_name = ""
        self.avatar = ""
        self.foreign_id = ""
        self.unique_id = ""

    def store(self):
        pass


class Source(BaseModel):
    def __init__(self):
        self.id = 0
        self.channel_id = 0
        self.second_channel_id = 0
        self.name = ""
        self.state = 0

    def select(self):
        pass
