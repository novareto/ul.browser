# -*- coding: utf-8 -*-

import os
from setuptools import setup, find_packages


def read(*rnames):
    return open(
        os.path.join(
            os.path.join(os.path.dirname(__file__), 'docs'),
            *rnames)).read()

version = '0.4'
long_description = read('README.txt') + '\n' + read('HISTORY.txt')

install_requires = [
     "IPython >= 2.3",
     "cromlech.browser",
     "cromlech.configuration",
     "cromlech.dawnlight",
     "cromlech.i18n",
     "cromlech.webob",
     "cromlech.wsgistate",
     "dawnlight",
     "dolmen.forms.base",
     "dolmen.forms.crud",
     "dolmen.forms.table",
     "dolmen.forms.viewlet",
     "dolmen.forms.ztk",
     "dolmen.layout",
     "dolmen.location",
     "dolmen.menu",
     "dolmen.message",
     "dolmen.template",
     "dolmen.view",
     "dolmen.viewlet",
     "grokcore.component",
     "setuptools",
     "uvc.entities",
     "z3c.table",
     "zope.component",
     "zope.event",
     "zope.location",
    ]

tests_require = [
    ]

setup(
    name='ul.browser',
    version=version,
    author='Novareto GmbH',
    author_email='',
    url='http://www.novareto.de',
    download_url='http://pypi.python.org/pypi/ul.browser',
    description='Browser components for uvclight',
    long_description=long_description,
    license='ZPL',
    classifiers=[
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Zope Public License',
        'Programming Language :: Python',
        ],
    packages=find_packages('src'),
    package_dir={'': 'src'},
    namespace_packages=['ul'],
    include_package_data=True,
    zip_safe=False,
    install_requires=install_requires,
    tests_require=tests_require,
    extras_require={
        'test': tests_require
        },
    )
