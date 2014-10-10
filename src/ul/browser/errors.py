# -*- coding: utf-8 -*-
# Copyright (c) 2007-2013 NovaReto GmbH
# cklinger@novareto.de

import traceback

from .components import Page
from .utils import get_template

from cromlech.dawnlight import ITracebackAware
from dawnlight import ResolveError
from dolmen.view.components import query_view_layout
from grokcore.component import name, context
from zope.interface import implementer
from zope.location import locate, Location


def make_error_layout_response(view, result, name=None):
    if name is None:
        name = getattr(view, 'layoutName', "")
    layout = query_view_layout(view, name=name)
    if layout is not None:
        wrapped = layout(result, **{'view': view})
        response = view.responseFactory()
        response.write(wrapped or u'')
    else:
        response = view.responseFactory()
        response.write(result or u'')
    return response


class Error404(Location):

    def __init__(self, context):
        self.context = context
        locate(self, context.__parent__, context.__name__)

    @property
    def title(self):
        return u"Not found"

    @property
    def description(self):
        return str(self.context)


@implementer(ITracebackAware)
class PageError404(Page):
    name('')
    context(ResolveError)
    make_response = make_error_layout_response

    template = get_template('404.cpt', __file__)

    def __init__(self, context, request):
        self.context = Error404(context)
        self.request = request

    def set_exc_info(self, exc_info):
        self.traceback = ''.join(traceback.format_exception(*exc_info))


class Error500(Location):

    def __init__(self, context):
        self.context = context
        locate(self, context.__parent__, context.__name__)

    @property
    def title(self):
        return u"Server error"

    @property
    def description(self):
        return str(self.context)


@implementer(ITracebackAware)
class PageError500(Page):
    name('')
    context(Exception)
    make_response = make_error_layout_response

    template = get_template('500.cpt', __file__)

    def __init__(self, context, request):
        self.context = Error500(context)
        self.request = request

    def set_exc_info(self, exc_info):
        self.traceback = ''.join(traceback.format_exception(*exc_info))
