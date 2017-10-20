# coding:utf-8

import datetime


def format_insert_sql(table, fields, returns):
    keys = ", ".join(fields)
    return_str = ""
    values = ("%s," * len(fields)).strip(",")
    if len(returns) != 0:
        return_str = "RETURNING %s" % (", ".join(returns))

    return "INSERT INTO %s (%s) VALUES (%s) %s;" % (table, keys, values, return_str)


def format_select_sql(table, fields, params):
    pass


def format_update_sql(table, fields, params, returns):
    pass


def format_delete_sql(table, params, returns):
    pass


def get_default_time():
    time_now = datetime.datetime.now()
    return time_now


if __name__ == "__main__":
    print format_insert_sql("test_table", ["1", "s", "3"], ["3"])
