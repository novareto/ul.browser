# -*- coding: utf-8 -*-

from cromlech.wsgistate import WsgistateSession


def sessionned(key):
    def session_wrapped(wrapped):
        def caller(environ, start_response):
            with WsgistateSession(environ, key):
                return wrapped(environ, start_response)
        return caller
    return session_wrapped
