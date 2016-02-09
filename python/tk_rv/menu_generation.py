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
import sys
import os
import unicodedata

import rv.commands
import rv.qtutils

from tank.platform.qt import QtGui, QtCore
from .app_command import AppCommand

class MenuGenerator(object):
    def __init__(self, engine):
        self._engine = engine

    @property
    def engine(self):
        return self._engine

    def create_menu(self):
        self.engine.log_debug("INFO: create_menu.")

        self._menu_handle = []

        sgtk_menu = [(self.engine.menu_name, [("_", None)])]
        rv.commands.defineModeMenu(self.engine.toolkit_rv_mode_name, sgtk_menu)

        self._context_menu = self._add_context_menu()
        self._menu_handle.append(self._context_menu)

        separator_item = ("_", None)
        self._menu_handle.append(separator_item)

        menu_items = []

        for (cmd_name, cmd_details) in self.engine.commands.items():
            menu_items.append(AppCommand(cmd_name, cmd_details))

        menu_items.sort(key=lambda x: x.name)

        # add favourites to the menu
        for fav in self.engine.get_setting("menu_favourites", []):
            app_instance_name = fav["app_instance"]
            menu_name = fav["name"]
            for cmd in menu_items:
                if cmd.get_app_instance_name() == app_instance_name and cmd.name == menu_name:
                    menu_item = cmd.define_menu_item()
                    self._menu_handle.append(menu_item)
                    cmd.favourite = True

        # add separator
        self._menu_handle.append(separator_item)
        self.engine.log_debug("create_menu seperator")

        # separate menu items out into various sections
        commands_by_app = {}
        for cmd in menu_items:
            if cmd.get_type() == "context_menu":
                pass
            else:
                app_name = cmd.get_app_name()
                if app_name is None:
                    app_name = "Other Items"
                if not app_name in commands_by_app:
                    commands_by_app[app_name] = []
                menu_item = cmd.define_menu_item()
                commands_by_app[app_name].append(menu_item)

        # add app-specific menus to the menu handle
        for menu_name, menu_items in commands_by_app.iteritems():
            self._menu_handle.append((menu_name, menu_items))

        # update sgtk menu
        sgtk_menu = [(self.engine.menu_name, self._menu_handle)]
        rv.commands.defineModeMenu(self.engine.toolkit_rv_mode_name, sgtk_menu)
        self.engine.log_debug("create_menu done.")

    def destroy_menu(self):
        self.engine.log_debug("destroy_menu: %r." % self)

        #self.engine._on_dialog_closed(self._sg_tk_test)
        self.engine.__qt_widget_trash.append(self._sg_tk_test)

        sgtk_menu = [("", [("_", None)])]
        rv.commands.defineModeMenu(self.engine.toolkit_rv_mode_name, sgtk_menu)

    ##########################################################################################
    # context menu and UI

    def _add_context_menu(self):
        ctx = self.engine.context
        ctx_name = str(ctx)
        return (ctx_name, [])

        