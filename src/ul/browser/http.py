# -*- coding: utf-8 -*-

import threading


http_locals = threading.local()
http_locals.request = None


def setRequest(request=None):
    http_locals.request = request


def getRequest():
    return http_locals.request
