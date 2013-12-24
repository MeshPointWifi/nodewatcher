import copy
import re

from django.conf import settings
from django.utils import translation

from . import exceptions

# Exports
__all__ = [
    'Menu',
    'MenuEntry',
    'ugettext_lazy',
    'menus'
]

VALID_NAME = re.compile('^[A-Za-z_][A-Za-z0-9_]*$')


def ugettext_lazy(message):
    translated = translation.ugettext_lazy(message)
    translated.message = message
    return translated


class MenuEntry(object):
    def __init__(self, label=None, url=None, permission_check=None, order=0):
        if isinstance(label, basestring):
            self._name = label
            self._label = label
        elif getattr(label, 'message'):
            self._name = label.message
            self._label = label
        else:
            raise exceptions.InvalidMenuEntry("Menu entry label must be a string or translated with nodewatcher.frontend.components.ugettext_lazy")

        self._url = url
        self._permission_check = permission_check
        self._order = order
        self._context = None

    def get_label(self):
        return self._label

    def get_url(self):
        if callable(self._url):
            return self._url(self._context)
        else:
            return self._url

    def has_permission(self, request):
        return not self._permission_check or self._permission_check(request, self)

    def get_order(self):
        return self._order

    def add_context(self, context):
        with_context = copy.copy(self)
        with_context._context = context
        return with_context


class Menu(object):
    def __init__(self, name):
        if not name:
            raise exceptions.InvalidMenu("A menu has invalid name")

        if not VALID_NAME.match(name):
            raise exceptions.InvalidMenu("A menu '%s' has invalid name" % name)

        self._name = name
        self._entries = []

    def get_name(self):
        return self._name

    def add(self, entry_or_iterable):
        if not hasattr(entry_or_iterable, '__iter__'):
            entry_or_iterable = [entry_or_iterable]

        for entry in entry_or_iterable:
            if not isinstance(entry, MenuEntry):
                raise exceptions.InvalidMenuEntry("'%s' class is not an instance of nodewatcher.core.frontend.components.MenuEntry" % entry.__name__)

            self._entries.append(entry)

        self._sort_entries()

    def get_entries(self):
        return self._entries

    def _sort_entries(self):
        order = getattr(settings, 'MENU_%s_ORDER' % self.get_name().upper(), [])

        def setting_label(setting):
            if isinstance(setting, basestring):
                return setting
            else:
                return setting['label']

        def setting_order(setting, order):
            if isinstance(setting, basestring):
                return {
                    'label': setting,
                    'order': order,
                }
            else:
                setting['order'] = order
                return setting

        order_dict = dict([(setting_label(setting), setting_order(setting, order)) for (order, setting) in enumerate(order)])

        # Remove hidden entries
        self._entries = [entry for entry in self._entries if not order_dict.get(entry._name, {}).get('hide', False)]

        def sort_key(entry):
            return order_dict.get(entry._name, {}).get('order', -1), entry._order, entry._name

        # Sort entries by settings, entry order, or name
        self._entries.sort(key=sort_key, reverse=True)


class Menus(object):
    def __init__(self):
        self._menus = {}
        self._states = []

    def __enter__(self):
        self._states.append(copy.copy(self._menus))

    def __exit__(self, exc_type, exc_val, exc_tb):
        state = self._states.pop()

        if exc_type is not None:
            # Reset to the state before the exception so that future
            # calls do not raise MenuNotRegistered or
            # MenuAlreadyRegistered exceptions
            self._menus = state

        # Re-raise any exception
        return False

    def register(self, menu_or_iterable):
        if not hasattr(menu_or_iterable, '__iter__'):
            menu_or_iterable = [menu_or_iterable]

        for menu in menu_or_iterable:
            if not isinstance(menu, Menu):
                raise exceptions.InvalidMenu("'%s' class is not an instance of nodewatcher.core.frontend.components.Menu" % menu.__name__)

            menu_name = menu.get_name()

            if not VALID_NAME.match(menu_name):
                raise exceptions.InvalidMenu("A menu '%s' has invalid name" % menu_name)

            if menu_name in self._menus:
                raise exceptions.MenuAlreadyRegistered("A menu with name '%s' is already registered" % menu_name)

            self._menus[menu_name] = menu

    def unregister(self, menu_or_iterable):
        if not hasattr(menu_or_iterable, '__iter__'):
            menu_or_iterable = [menu_or_iterable]

        for menu in menu_or_iterable:
            menu_name = menu.get_name()

            if menu_name not in self._menus:
                raise exceptions.MenuNotRegistered("No menu with name '%s' is registered" % menu_name)

            del self._menus[menu_name]

    def get_all_menus(self):
        return self._menus.values()

    def get_menu(self, menu_name):
        try:
            return self._menus[menu_name]
        except KeyError:
            raise exceptions.MenuNotRegistered("No menu with name '%s' is registered" % menu_name)

    def has_menu(self, menu_name):
        return menu_name in self._menus

menus = Menus()