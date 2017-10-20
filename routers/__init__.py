from urlparse import urljoin
from .api_doc import routers as api_doc_routers
from .store import routers as store_routers
from .update import routers as update_routers
from .base import routers as base_routers

service_routers = []


def register_url(path_prefix, routers):
    for router in routers:
        item = []
        item.append(urljoin(path_prefix, router[0]))
        item.extend(router[1:])
        service_routers.append(tuple(item))


register_url("/", base_routers)
register_url("/api_doc/", api_doc_routers)
register_url("/api/", base_routers)
register_url("/api/store/", store_routers)
register_url("/api/update/", update_routers)
