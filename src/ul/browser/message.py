# -*- coding: utf-8 -*-

import uuid
import grokcore.component as grok
from cromlech.browser import IRequest, getSession
from dolmen.message import interfaces
from zope.interface import implements


class SessionSource(grok.GlobalUtility):
    """A message source storing messages into the session.
    """
    grok.context(IRequest)
    grok.implements(interfaces.IMessageSource)

    _key = u'dolmen.message.session'

    def send(self, text, type=interfaces.BASE_MESSAGE_TYPE):
        session = getSession()
        if session is None:
            return False
        messages = session.get(self._key, [])
        messages.append(
            {"message": text, "type": type, "uid": str(uuid.uuid4())}
        )
        session[self._key] = messages
        return True

    def __len__(self):
        session = getSession()
        return len(session.get(self._key, []))

    def __iter__(self):
        session = getSession()
        if session is None or self._key not in session:
            return iter([])
        return iter(session[self._key])

    def remove(self, item):
        session = getSession()
        if session is None or self._key not in session:
            raise ValueError("No session")
        session[self._key].remove(item)


class MessageReceiver(grok.Adapter):
    """A receiver that can receive from any source.
    """
    grok.context(interfaces.IMessageSource)
    implements(interfaces.IMessageReceiver)

    def receive(self, type=None):
        messages = list(self.context)  # copy as we will mutate
        for message in messages:
            if (type and message['type'] == type) or not type:
                yield message
                self.context.remove(message)
