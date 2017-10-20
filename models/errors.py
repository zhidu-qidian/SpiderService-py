# coding:utf-8


class NoSuchObjectError(Exception):
    def __init__(self, value=None):
        if not value:
            self.value = "No Such Object"
        else:
            assert isinstance(value, str)
            self.value = value

    def __unicode__(self):
        return self.value

    def __str__(self):
        return self.value
