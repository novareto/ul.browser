# -*- coding: utf-8 -*-

from cromlech.browser import IURL
from cromlech.events import ObjectCreatedEvent

from dolmen.forms.base import Action, SuccessMarker
from dolmen.forms.base.markers import FAILURE
from dolmen.forms.base.utils import set_fields_data, apply_data_event
from dolmen.forms.crud import actions, i18n as _
from dolmen.forms.crud.actions import CancelAction  # unchanged


class BaseAction(Action):

    def __init__(self, title=None, identifier=None, successMessage=None,
                 failureMessage=None, **htmlAttributes):
        super(BaseAction, self).__init__(title, identifier, **htmlAttributes)
        self.failureMessage = failureMessage
        self.successMessage = successMessage


class AddAction(BaseAction):
    """Add action for an IAdding context.
    """
    successMessage = _(u"Content created")
    failureMessage = _(u'Adding failed')
    
    def __init__(self, *args, **kwargs):
        self.factory = kwargs.pop('factory')
        super(AddAction, self).__init__(title)
    
    def __call__(self, form):
        data, errors = form.extractData()
        if errors:
            form.submissionError = errors
            return FAILURE

        obj = self.factory()
        set_fields_data(form.fields, obj, data)
        notify(ObjectCreatedEvent(obj))
        form.context.add(obj)

        message(self.successMessage)
        url = str(IURL(obj, form.request))
        return SuccessMarker('Added', True, url=url)


class UpdateAction(BaseAction):
    """Update action for any locatable object.
    """
    successMessage = _(u"Content updated")
    failureMessage = _(u'Updated failed')

    def __call__(self, form):
        data, errors = form.extractData()
        if errors:
            form.submissionError = errors
            return FAILURE

        apply_data_event(form.fields, form.getContentData(), data)
        message(self.successMessage)
        url = str(IURL(form.context, form.request))
        return SuccessMarker('Updated', True, url=url)


class DeleteAction(actions.DeleteAction, BaseAction):
    """Delete action for any locatable context.
    """
    pass
