# -*- coding: utf-8 -*-

import os
import logging
from cromlech.configuration.utils import load_zcml
from cromlech.i18n import register_allowed_languages
from cromlech.browser import setSession
from cromlech.wsgistate import WsgistateSession

logger = logging.getLogger('ul.browser')


session_managers = {
    'wsgistate': WsgistateSession,
}


def sessionned(key, plugin=None):
    def session_wrapped(wrapped):
        def caller(environ, start_response):
            if plugin is None:
                session = environ.get(key)
                setSession(session)
                response = wrapped(environ, start_response)
                setSession(None)
                return response
            else:
                manager = session_managers.get(plugin)
                if manager is None:
                    raise NotImplementedError('Unknown session plugin "%s"' % plugin)
                else:
                    with manager(environ, key):
                        response = wrapped(environ, start_response)
                        return response
        return caller
    return session_wrapped


def with_zcml(arg_name, method='pop'):
    def zcml_runner(func):
        def zcml_loader(*args, **kwargs):
            if arg_name in kwargs:
                filename = getattr(kwargs, method)(arg_name)
                assert filename and isinstance(filename, (str, unicode))
                load_zcml(filename)
            else:
                logger.warning('No zcml argument %r found.' % arg_name)
            return func(*args, **kwargs)
        return zcml_loader
    return zcml_runner


def with_i18n(arg_name, fallback, method='pop'):
    def i18n_runner(func):
        def i18n_loader(*args, **kwargs):
            languages = getattr(kwargs, method)(arg_name, fallback)
            assert languages and isinstance(languages, (str, unicode))
            allowed = languages.strip().replace(',', ' ').split()
            register_allowed_languages(allowed)
            return func(*args, **kwargs)
        return i18n_loader
    return i18n_runner
