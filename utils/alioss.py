# coding:utf-8

import hashlib
import requests
import oss2
from configs import SETTINGS


def fetch(url, referer="", timeout=60):
    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.100 Safari/537.36"
    if len(referer) < 11:
        referer = None
    headers = {
        "User-Agent": user_agent,
        "Referer": referer
    }
    try:
        req = requests.get(url, headers=headers, timeout=timeout)
    except Exception as e:
        return None
    else:
        return req


def get_bucket(bucket_name):
    access_key_id = SETTINGS["oss_accessid"]
    access_key_secret = SETTINGS["oss_accesskey"]
    region = SETTINGS["oss_endpoint"]
    auth = oss2.Auth(access_key_id, access_key_secret)
    bucket = oss2.Bucket(auth, region, bucket_name)
    return bucket


def upload_file(bucket_name, target_name, data):
    bucket = get_bucket(bucket_name)
    try:
        respond = bucket.put_object(target_name, data)
    except Exception as e:
        print "upload image exception"
        return False
    if respond.status != 200:
        print "upload image to oss error: %s" % respond.status
        return False
    return True


def delete_file(bucket_name, file_name):
    bucket = get_bucket(bucket_name)
    try:
        bucket.delete_object(file_name)
    except Exception as e:
        print e
        return False
    else:
        return True


def upload_img(url, referer=""):
    img_bucket_name = "bdp-images"
    img_bucket_domain = "http://pro-pic.deeporiginalx.com"
    # img_bucket_path = "https://oss-cn-hangzhou.aliyuncs.com/bdp-images/"
    req = fetch(url, referer)
    if not req:
        return
    try:
        img_content = req.content
        uid = get_unique_id(img_content)
    except Exception as e:
        return e
    content_type = req.headers.get("Content-Type", "").lower()
    suffix_map = {
        "image/jpeg": "jpg",
        "image/webp": "webp",
        "image/png": "png",
        "image/gif": "gif",
        "image/bmp": "bmp"
    }
    suffix = suffix_map.get(content_type, "")
    if suffix == "":
        print "Can't download image: %s" % content_type
        return Exception()
    object_key = "%s.%s" % (uid, suffix)
    result = upload_file(img_bucket_name, object_key, img_content)
    if result:
        img_url = "%s/%s" % (img_bucket_domain, object_key)
        return img_url
    else:
        return Exception()


def delete_img(object_key):
    img_bucket_name = "bdp-images"
    result = delete_file(img_bucket_name, object_key)
    if result:
        return True
    else:
        return False


def get_unique_id(buffer):
    sh = hashlib.sha256()
    sh.update(buffer)
    code_str = str(sh.hexdigest())
    return code_str


if __name__ == "__main__":
    print upload_img(url="http://jbcdn2.b0.upaiyun.com/2016/06/67a155d2312e853237b0b7b0cf62b5d3.png", referer="")
