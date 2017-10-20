# coding:utf-8
"""
自动生成API接口文档
"""
import sys
import os
import re
import shutil
import inspect
import yaml

try:
    import mkdocs
except ImportError:
    mkdocs = None


class NotionParser(object):
    param_re = re.compile(':param (.*?):(.*?)')
    note_re = re.compile(':note:(.*?)')
    return_re = re.compile(':return (.*?):(.*?)')

    @classmethod
    def get_param(cls, line):
        return cls.param_re.findall(line)

    @classmethod
    def get_note(cls, line):
        return cls.note_re.findall(line)

    @classmethod
    def get_return(cls, line):
        return cls.return_re.findall(line)

    @classmethod
    def get_notion(cls, notion):
        notion_meta = {
            "desc": [],
            "note": [],
            "params": [],
            "return": []
        }
        for line in notion.split("\n"):
            check_note = cls.get_note(line)
            check_param = cls.get_param(line)
            check_return = cls.get_return(line)
            if check_note:
                notion_meta["note"].append(check_note[0])
            elif check_param:
                notion_meta["params"].append({
                    check_param[0][0]: check_param[0][1]})
            elif check_return:
                notion_meta["return"].append({
                    check_return[0][0]: check_return[0][1]
                })
            else:
                strip_text = line.strip()
                if strip_text and not re.match(':.*?:', strip_text):
                    notion_meta["desc"].append(strip_text)
        return notion_meta


class BaseGenerator(object):
    doc_path = "../api_doc"
    doc_path_abs = ""
    method_list = ["get", "post", "put", "delete", "head", "connect", "options", "trace"]
    api_level_re = re.compile('/api/(.*?)/\S+')

    def gen(self, urls):
        urls = self._filter_api(urls)
        meta = self.get_meta(urls)
        self.export(meta=meta)

    def get_out_put_dir(self):
        if self.doc_path_abs:
            return self.doc_path_abs
        current_path = os.path.dirname(__file__)
        doc_path_rel = os.path.join(current_path, self.doc_path)
        self.doc_path_abs = os.path.abspath(doc_path_rel)
        return self.doc_path_abs

    def _filter_api(self, urls):
        urls = filter(lambda x: re.match('/api/(.+?)', x[0]), urls)
        urls = sorted(urls, key=lambda x: x[0], reverse=True)
        return urls

    def get_methods(self, url):

        methods = list()
        for method in self.method_list:
            _class = url[1]
            if method in url[1].__dict__.keys() and inspect.ismethod(eval("_class." + method)):
                item = dict()
                item["method"] = method
                desc = eval("_class." + method).__doc__
                desc = desc.strip() if desc else ""
                item["notion"] = NotionParser.get_notion(desc)
                methods.append(item)

        return methods

    def get_meta(self, urls):
        meta = []
        for url in urls:
            item = dict()
            item["api"] = url[0]
            item["methods"] = self.get_methods(url)
            item["handler"] = url[1].__name__
            desc = url[1].__doc__
            item["desc"] = desc.strip() if desc else ""
            meta.append(item)
        apis = {
            "ungroup": meta,
            "group": dict()
        }
        for item in meta:
            api = item["api"]
            api_level = self.api_level_re.findall(api)[0]
            apis["group"].setdefault(api_level, [])
            apis["group"][api_level].append(item)
        group = sorted(apis["group"].items(), key=lambda x: x[0])
        group = [{i[0]: i[1]} for i in group]
        apis["group"] = group
        return apis

    def check_create_dir(self, path):
        try:
            if os.path.exists(path):
                shutil.rmtree(path, ignore_errors=True)
        except Exception as e:
            print e
            return False
        else:
            return True

    def get_md_content(self, apis):
        content = ""
        for num ,api in enumerate(apis):
            print api
            api_url = api["api"]
            content += "## "+str(num+1)+"`" + api_url + "`\n"
            api_desc = api["desc"]
            content += "接口描述：\n"
            content += "> " + api_desc.strip() + "\n\n"
            api_methods = api["methods"]
            for api_method in api_methods:
                content += "`" +api_method["method"] + "`\n\n"
                content += "+ 描述：" + ";".join(api_method["notion"]["desc"]) + "\n"
                content += "+ 注意事项：" + ";".join(api_method["notion"]["note"]) + "\n"
                content += "+ 参数：\n"
                for param in api_method["notion"]["params"]:
                    key = param.keys()[0]
                    content += "    + `" + key + "`:" + param[key]+"\n"
                content += "+ 返回值：\n"
                for r in api_method["notion"]["return"]:
                    key = r.keys()[0]
                    content += "    + `" + key + "`:" + r[key]
        return content

    def export(self, **kwargs):
        meta = kwargs.get("meta", {})
        print meta["group"]


class MkdocsGenerator(BaseGenerator):
    yml_file_name = "mkdocs.yml"

    def export(self, **kwargs):
        meta = kwargs.get("meta", {})
        apis = meta.get("group", [])
        doc_path = self.get_out_put_dir()
        self.check_create_dir(doc_path)
        os.system("mkdocs new %s" % doc_path)
        self.config_yml(apis)
        self.config_detail_content(apis)
        self.config_index_content(apis)
        os.chdir(doc_path)
        os.system("mkdocs build")

    def config_detail_content(self, apis):
        for group in apis:
            key = group.keys()[0]
            doc_path = self.get_out_put_dir()
            content_path = os.path.join(doc_path, "docs/" + key + ".md")
            with open(content_path, "wb") as f:
                content_text = self.get_md_content(group[key])
                f.write(content_text)

    def config_index_content(self, apis):
        index_content = """
# 欢迎浏览SpiderService Api 文档
API列表如下，可通过侧边栏/顶部目录进行浏览搜索：
        """
        for group in apis:
            key = group.keys()[0]
            index_content += "\n### `" + key + "`相关Api\n"
            for api in group[key]:
                index_content += "+ " + api["api"] + "\n"
        doc_path = self.get_out_put_dir()
        index_path = os.path.join(doc_path, "docs/" + "index.md")
        with open(index_path, "wb") as f:
            f.write(index_content)

    def config_yml(self, apis):
        doc_path = self.get_out_put_dir()
        yml_file_path = os.path.join(doc_path, self.yml_file_name)
        yml_dict = {
            "site_name": "SpiderServers API Doc",
            "pages": [{"Home": "index.md"}]

        }
        for group in apis:
            key = group.keys()[0]
            content_name = "%s.md" % key
            yml_dict["pages"].append({
                key: content_name
            })

        yml_text = yaml.dump(yml_dict)
        yml_text = re.sub('\{|\}|\"', "", yml_text)
        with open(yml_file_path, "wb") as f:
            f.write(yml_text)


def gen_api_doc(app):
    urls = app.urls
    print "mkdocs exists,using it to gen docs"
    MkdocsGenerator().gen(urls)
    # print "mkdocs not exists,gen simple markdown docs"
    # BaseGenerator().gen(urls)


if __name__ == "__main__":
    MkdocsGenerator().get_yml()
