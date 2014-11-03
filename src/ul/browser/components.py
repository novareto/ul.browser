# -*- coding: utf-8 -*-

from .utils import make_json_response, url as compute_url, get_template

from cromlech.browser import ITemplate
from cromlech.browser.exceptions import HTTPFound
from cromlech.browser.exceptions import REDIRECTIONS
from cromlech.webob.response import Response
from dolmen.forms import crud
from dolmen.forms.base import Form as BaseForm
from dolmen.forms.base import action
from dolmen.forms.base.interfaces import IForm, IModeMarker
from dolmen.forms.base.markers import HiddenMarker
from dolmen.forms.table import TableForm as BaseTableForm
from dolmen.forms.viewlet import ViewletForm
from dolmen.forms.ztk.validation import InvariantsValidation
from dolmen.layout import Layout as BaseLayout
from dolmen.location import get_absolute_url
from dolmen.menu import IMenu, Menu as BaseMenu, Entry as MenuItem
from dolmen.menu import menu
from dolmen.message import BASE_MESSAGE_TYPE
from dolmen.message.utils import send
from dolmen.view import View as BaseView, make_layout_response
from dolmen.viewlet import slot as viewletmanager
from grokcore.component import adapter, implementer
from grokcore.component import order, baseclass, name, title, context
from uvc.design.canvas import ISubMenu, IContextualActionsMenu
from z3c.table.column import LinkColumn, ModifiedColumn, CheckBoxColumn
from z3c.table.table import Table as BaseTable
from zope.component import getMultiAdapter, getAdapters
from zope.event import notify
from zope.interface import Interface
import zope.lifecycleevent


class View(BaseView):
    baseclass()
    context(Interface)
    responseFactory = Response

    def url(self, obj, name=None, data=None):
        """This function does something.

        Args:
            obj (object):  The ILocation providing object.

        Kwargs:
            name (str): .
            data (dict): .

        Returns:
            str.

        """
        return compute_url(self.request, obj, name, data)

    def application_url(self):
        return self.request.application_url

    def flash(self, message, type=BASE_MESSAGE_TYPE):
        return send(message, type=type)

    def redirect(self, url, code=302):
        exception = REDIRECTIONS[code]
        raise exception(url)


class Layout(BaseLayout):
    baseclass()
    context(Interface)
    responseFactory = Response


class Page(View):
    baseclass()
    make_response = make_layout_response


class Index(Page):
    baseclass()
    name('index')
    make_response = make_layout_response


class JSON(View):
    baseclass()
    make_response = make_json_response


class Menu(BaseMenu):
    baseclass()
    css = "nav"

    submenus = None

    def update(self):
        self.submenus = list()
        BaseMenu.update(self)
        submenus = getAdapters(
            (self.context, self.request, self.view, self), ISubMenu)
        for id, submenu in submenus:
            submenu.update()
            self.submenus.append(submenu)


class SubMenu(Menu):
    baseclass()
    context(Interface)
    viewletmanager(IMenu)

    def __init__(self, context, request, view, parentmenu=None):
        Menu.__init__(self, context, request, view)
        self.parentmenu = parentmenu

    def update(self):
        BaseMenu.update(self)


class Form(BaseForm):
    baseclass()
    context(Interface)
    responseFactory = Response
    make_response = make_layout_response
    dataValidators = [InvariantsValidation]

    template = None

    def url(self, obj, name=None, data=None):
        return compute_url(self.request, obj, name, data)

    def application_url(self):
        return self.request.application_url

    def flash(self, message, type=BASE_MESSAGE_TYPE):
        return send(message, type=type)

    def namespace(self):
        namespace = super(Form, self).namespace()
        namespace['macro'] = self.getTemplate().macros
        return namespace

    def redirect(self, url, code=302):
        exception = REDIRECTIONS[code]
        raise exception(url)

    def isHidden(self, widget):
        mode = widget.component.mode
        return IModeMarker.providedBy(mode) and isinstance(HiddenMarker, mode)

    def getTemplate(self):
        template = getMultiAdapter((self, self.request), ITemplate)
        return template

    def render(self):
        """Template is taken from the template attribute or searching
        for an adapter to ITemplate for entry and request
        """
        template = getattr(self, 'template', None)
        if template is None:
            template = getMultiAdapter((self, self.request), ITemplate)
        return template.render(
            self, target_language=self.target_language, **self.namespace())


class ViewletForm(ViewletForm):
    baseclass()

    def namespace(self):
        namespace = super(ViewletForm, self).namespace()
        namespace['macro'] = self.getTemplate().macros
        return namespace

    def getTemplate(self):
        template = getMultiAdapter((self, self.request), ITemplate)
        return template


form_template = get_template('form.cpt', __file__)


@adapter(IForm, Interface)
@implementer(ITemplate)
def adapter_form_template(context, request):
    """default template for a form
    """
    return form_template


class AddForm(Form):
    title(u'Erstellen')
    _finishedAdd = False

    @action(u'Speichern', identifier="uvcsite.add")
    def handleAdd(self):
        data, errors = self.extractData()
        if errors:
            self.flash('Es sind Fehler aufgetreten')
            return
        obj = self.createAndAdd(data)
        if obj is not None:
            # mark only as finished if we get the new object
            self._finishedAdd = True

    def createAndAdd(self, data):
        obj = self.create(data)
        notify(zope.lifecycleevent.ObjectCreatedEvent(obj))
        self.add(obj)
        return obj

    def create(self, data):
        raise NotImplementedError

    def add(self, object):
        raise NotImplementedError

    def nextURL(self):
        raise NotImplementedError

    def render(self):
        if self._finishedAdd:
            raise HTTPFound(self.nextURL())
            self.request.response.redirect(self.nextURL())
            return ""
        return super(AddForm, self).render()


class EditForm(crud.Edit, Form):
    title(u'Bearbeiten')
    baseclass()


class EditMenuItem(MenuItem):
    menu(IContextualActionsMenu)
    title(u'Bearbeiten')
    name('edit')
    order(20)


class DisplayForm(crud.Display, Form):
    title(u'Anzeigen')
    baseclass()


class DefaultView(DisplayForm):
    name('index')
    title(u'Anzeigen')
    baseclass()
    responseFactory = Response
    make_response = make_layout_response


class DisplayMenuItem(MenuItem):
    menu(IContextualActionsMenu)
    title(u'Anzeigen')
    name('index')
    order(10)


class DeleteForm(crud.Delete, Form):
    title(u'Entfernen')
    baseclass()


class DeleteMenuItem(MenuItem):
    menu(IContextualActionsMenu)
    title('Entfernen')
    name('delete')
    order(30)


class Table(BaseTable):

    def getBatchSize(self):
        return int(self.request.form.get(
            self.prefix + '-batchSize', self.batchSize))

    def getBatchStart(self):
        return int(self.request.form.get(
            self.prefix + '-batchStart', self.batchStart))

    def getSortOn(self):
        """Returns sort on column id.
        """
        return self.request.form.get(self.prefix + '-sortOn', self.sortOn)

    def getSortOrder(self):
        """Returns sort order criteria.
        """
        return self.request.form.get(
            self.prefix + '-sortOrder', self.sortOrder)


class TableView(Table, View):
    baseclass()
    context(Interface)

    def update(self):
        Table.update(self)


class TablePage(Table, Page):
    baseclass()
    context(Interface)

    def update(self):
        Table.update(self)

    def render(self):
        if self.template:
            return self.template.render(
                self, target_language=self.target_language, **self.namespace())
        return self.renderTable()


class LinkColumn(LinkColumn):
    baseclass()

    def getLinkURL(self, item):
        """Setup link url."""
        if self.linkName is not None:
            return '%s/%s' % (
                get_absolute_url(item, self.request), self.linkName)
        return get_absolute_url(item, self.request)


class CheckBoxColumn(CheckBoxColumn):
    baseclass()

    def isSelected(self, item):
        v = self.request.form.get(self.getItemKey(item), [])
        if not isinstance(v, list):
            # ensure that we have a list which prevents to compare strings
            v = [v]
        if self.getItemValue(item) in v:
            return True
        return False


class ModifiedColumn(ModifiedColumn):
    baseclass()


class TableForm(BaseTableForm):
    baseclass()
    context(Interface)

    responseFactory = Response
    make_response = make_layout_response
