# -*- coding: utf-8 -*-

from .decorators import with_zcml, with_i18n, sessionned
from .context import ContextualRequest
from .shell import make_shell

from cromlech.dawnlight import DawnlightPublisher, ViewLookup
from cromlech.dawnlight import view_locator, query_view
from cromlech.dawnlight.lookup import ModelLookup
from zope.component.hooks import setSite
from zope.component.interfaces import IObjectEvent
from zope.event import notify
from zope.interface import Attribute, implementer


class IModelFoundEvent(IObjectEvent):
    request = Attribute("The current request")


class IBeforeTraverseEvent(IObjectEvent):
    request = Attribute("The current request")


@implementer(IBeforeTraverseEvent)
class BeforeTraverseEvent(object):

    def __init__(self, ob, request):
        self.object = ob
        self.request = request


@implementer(IModelFoundEvent)
class ModelFoundEvent(object):

    def __init__(self, ob, request):
        self.object = ob
        self.request = request


class UVCModelLookup(ModelLookup):

    def __call__(self, request, obj, stack):
        """Traverses following stack components and starting from obj.
        """
        unconsumed = stack[:]
        while unconsumed:
            for consumer in self.lookup(obj):
                any_consumed, obj, unconsumed = consumer(
                    request, obj, unconsumed)
                if any_consumed:
                    notify(BeforeTraverseEvent(obj, request))
                    break
            else:
                break

        notify(ModelFoundEvent(obj, request))
        return obj, unconsumed


located_view = ViewLookup(view_locator(query_view))
base_model_lookup = UVCModelLookup()


class Site(object):

    def __init__(self, model, name):
        self.model = model
        self.name = name

    def __enter__(self):
        root = self.model(self.name)
        setSite(root)
        return root

    def __exit__(self, exc_type, exc_value, traceback):
        setSite()


class Publication(object):

    layers = None

    @classmethod
    @with_zcml('zcml_file')
    @with_i18n('langs', fallback='en')
    def create(cls, gc, name, session_key):
        return cls(name, session_key)

    def __init__(self, name, session_key):
        self.publish = self.get_publisher()
        self.name = name
        self.session_key = session_key

    def get_publisher(
            self, view_lookup=located_view, model_lookup=base_model_lookup):
        publisher = DawnlightPublisher(model_lookup, view_lookup)
        return publisher.publish

    def get_credentials(self, environ):
        pass

    def principal_factory(self, username):
        pass

    def site_manager(self, environ):
        raise NotImplementedError

    def publish_traverse(self, request, site):
        publisher = self.get_publisher()
        return publisher(request, site)

    def __interact__(self, banner=u'', **namespace):
        return make_shell(banner=banner, **namespace)

    def __call__(self, environ, start_response):

        @sessionned(self.session_key)
        def publish(environ, start_response):
            layers = self.layers or list()
            with ContextualRequest(environ, layers=layers) as request:
                site_manager = self.site_manager(environ)
                with site_manager as site:
                    response = self.publish_traverse(request, site)
                    return response(environ, start_response)

        return publish(environ, start_response)
