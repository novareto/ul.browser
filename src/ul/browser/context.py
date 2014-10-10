# -*- coding: utf-8 -*-

from .http import setRequest
from cromlech import webob
from zope.interface import alsoProvides


class ContextualRequest(object):

    def __init__(self, environ, factory=webob.Request, layers=None):
        self.environ = environ
        self.factory = factory
        self.layers = layers or []

    def __enter__(self):
        request = self.factory(self.environ)
        for layer in self.layers:
            alsoProvides(request, layer)
        setRequest(request)
        return request

    def __exit__(self, type, value, traceback):
        setRequest()
