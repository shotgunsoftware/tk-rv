# Copyright (c) 2016 Shotgun Software Inc.
# 
# CONFIDENTIAL AND PROPRIETARY
# 
# This work is provided "AS IS" and subject to the Shotgun Pipeline Toolkit 
# Source Code License included in this distribution package. See LICENSE.
# By accessing, using, copying or modifying this work you indicate your 
# agreement to the Shotgun Pipeline Toolkit Source Code License. All rights 
# not expressly granted therein are reserved by Shotgun Software Inc.

import tank
import rv.commands
from tank.platform.qt import QtGui, QtCore

class MenuGenerator(object):
    def __init__(self, engine):
        """
        Initializes the menu generator for RV.

        :param engine:  The parent sgtk engine.
        """
        self.engine = engine
        self._menu_handle = []
        self._context_menu = None

    def create_menu(self):
        """
        Creates the top-level menu in RV and populates it with the
        context menu, plus any app commands that were registered
        with the engine.
        """
        self._context_menu = self._add_context_menu()
        self._menu_handle.append(self._context_menu)

        separator_item = ("_", None)
        self._menu_handle.append(separator_item)

        menu_commands = []

        # Wrap each command that was registered with the engine in
        # an AppCommand object. This will make it easy to then add
        # those commands to our menu in RV.
        for (cmd_name, cmd_details) in self.engine.commands.items():
            menu_commands.append(AppCommand(cmd_name, cmd_details))

        # All of the commands will be sorted by name in the menu.
        menu_commands.sort(key=lambda x: x.name)

        # Add a separator between the context menu and the rest
        # of the menu items.
        self._menu_handle.append(separator_item)

        # Separate the various menu items out into their sections.
        commands_by_app = dict()

        for cmd in menu_commands:
            menu_item = cmd.define_menu_item()

            if cmd.get_type() == "context_menu":
                self._add_item_to_context_menu(menu_item)
            else:
                app_name = cmd.get_app_name()

                if app_name not in commands_by_app:
                    commands_by_app[app_name] = []

                commands_by_app[app_name].append(menu_item)

        # Add app-specific menus to the menu handle.
        for menu_name, menu_items in commands_by_app.iteritems():
            self._menu_handle.append((menu_name, menu_items))

        # Create the main menu in RV.
        sgtk_menu = [(self.engine.menu_name, self._menu_handle)]
        rv.commands.defineModeMenu(self.engine.toolkit_rv_mode_name, sgtk_menu)

    def destroy_menu(self):
        """
        Tears down the top-level menu in RV.
        """
        sgtk_menu = [("", [("_", None)])]
        rv.commands.defineModeMenu(self.engine.toolkit_rv_mode_name, sgtk_menu)

    ##########################################################################################
    # context menu and UI

    def _add_context_menu(self):
        """
        Builds the context menu item that can then be added to
        an RV menu.
        """
        ctx = self.engine.context
        ctx_name = str(ctx)
        return (ctx_name, [])

    def _add_item_to_context_menu(self, item):
        """
        Adds the given menu item to the context menu. If the context
        menu has not been added to the menu generator, it will be prior
        to adding the new menu item to it.

        :param item:    The menu item to add to the context menu. This
                        takes the form of a tuple containing the command
                        name, its callback, and an optional hotkey to
                        associate with the action.
        """
        if not self._context_menu:
            self._add_context_menu()

        self._context_menu[1].append(item)


class AppCommand(object):
    """
    Wraps an engine command and provides convenience methods for
    adding that command to an RV menu.
    """
    def __init__(self, name, properties):
        """
        Initializes the AppCommand object.

        :param name:        The name to associate with the menu command.
        :param properties:  The command's properties dictionary. This is
                            the dictionary associated with the app command
                            as it was registered with the engine. See
                            Engine.register_command() for more details.
        """
        self.name = name
        self.properties = properties["properties"]
        self.callback = properties["callback"]

    def get_app_name(self):
        """
        Gets the name of the parent app that registered this command.
        """
        if "app" in self.properties:
            return self.properties["app"].display_name

        return

    def get_type(self):
        """
        Returns "node", "custom_pane" or "default"
        """
        return self.properties.get("type", "default")

    def define_menu_item(self):
        """
        Builds a menu item definition from the AppCommand. This item
        is structured as a tuple containing the command's name, callback,
        and an optional hotkey to associate with the item. This structure
        is what the RV menu system expects to receive.
        """
        hotkey = self.properties.get("hotkey")

        if hotkey:
            menu_item = (self.name, self.menu_item_callback, hotkey, None)
        else:
            menu_item = (self.name, self.menu_item_callback, None, None)

        return menu_item

    def menu_item_callback(self, event):
        """
        A wrapper method for the command's callback. This calls the
        callback function and disregards the event object that RV
        provides, as it is not necessary in our situation.

        :param event:   An RV event. This is disregarded, as it is not
                        necessary in the SGTK menu's situation.
        """
        self.callback()


        