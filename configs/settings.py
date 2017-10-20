# coding:utf-8


SETTINGS = dict()
SETTINGS["debug"] = True

# server
SETTINGS["server_host"] = "0.0.0.0"
SETTINGS["server_port"] = 8081

# pg
SETTINGS["pg_host"] = "公网IP" if SETTINGS["debug"] else "内网IP"
SETTINGS["pg_port"] = 5432
SETTINGS["pg_db"] = "BDP"
SETTINGS["pg_user"] = "postgres"
SETTINGS["pg_passwd"] = ""
SETTINGS["pg_maxconn"] = 10
SETTINGS["pg_maxidles"] = 3

# oss
SETTINGS["oss_endpoint"] = ""
SETTINGS["oss_accessid"] = ""
SETTINGS["oss_accesskey"] = ""



# ex_settings
# SETTINGS["template_path"] = os.path.join(os.path.dirname(__file__), "../templates")
# SETTINGS["static_path"] = os.path.join(os.path.dirname(__file__), "../static")
# SETTINGS["ui_modules"]={"Entry": EntryModule},
# SETTINGS["xsrf_cookies"]=True,
# SETTINGS["cookie_secret"]="xxxooo",
# SETTINGS["login_url"]="/auth/login",
