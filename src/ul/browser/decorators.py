# -*- coding: utf-8 -*-

from cromlech.configuration.utils import load_zcml
from cromlech.i18n import register_allowed_languages


def with_zcml(arg_name, method='pop'):
    def zcml_runner(func):
        def zcml_loader(*args, **kwargs):
            filename = getattr(kwargs, method)(arg_name)
            assert filename and isinstance(filename, (str, unicode))
            load_zcml(filename)
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