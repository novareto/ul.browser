# -*- coding: utf-8 -*-

import json
import urllib
from dolmen.location import get_absolute_url


def make_json_response(view, result, name=None):
    json_result = json.dumps(result)
    response = view.responseFactory()
    response.write(json_result)
    response.headers['Content-Type'] = 'application/json'
    return response


def url(request, obj, name=None, data=None):

    url = get_absolute_url(obj, request)
    if name is not None:
        url += '/' + urllib.quote(name.encode('utf-8'))

    if not data:
        return url

    if not isinstance(data, dict):
        raise TypeError('url() data argument must be a dict.')

    for k, v in data.items():
        if isinstance(v, unicode):
            data[k] = v.encode('utf-8')
        if isinstance(v, (list, set, tuple)):
            data[k] = [
                isinstance(item, unicode) and item.encode('utf-8')
                or item for item in v]

    return url + '?' + urllib.urlencode(data, doseq=True)
