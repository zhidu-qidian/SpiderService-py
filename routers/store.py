# coding:utf-8

import handlers
path_prefix = "/api/store/"
routers = [
    (r'video', handlers.StoreVideoHandler),
    (r'joke', handlers.StoreJokeHandler),
    (r'news', handlers.StoreNewsHandler),
    (r'comment', handlers.StoreCommentHnadler)
]
