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

class MenuGenerator(object):
    RV_MENU_SPACER = ("_", None)

    def __init__(self, engine):
        """
        Initializes the menu generator for RV.

        :param engine:  The parent sgtk engine.
        """
        self.engine = engine
        self._context_menu = None

    def create_menu(self):
        """
        Creates the top-level menu in RV and populates it with the
        context menu, plus any app commands that were registered
        with the engine.
        """
        self._context_menu = self._add_context_menu()

        # Wrap each command that was registered with the engine in
        # an AppCommand object. This will make it easy to then add
        # those commands to our menu in RV.
        menu_commands = [AppCommand(n, d) for n, d in self.engine.commands.items()]

        # All of the commands will be sorted by name in the menu.
        menu_commands.sort(key=lambda x: x.name)

        # Separate the various menu items out into their sections. We're
        # checking the menu_overrides setting and initializing a place for
        # each RV menu listed so that we can then organize the appropriate
        # commands into the requested menu.
        menu_overrides = self.engine.get_setting("menu_overrides", dict())

        # Note: dict comprehension is not available in Python 2.5. We are
        # safe here because all available versions of RV are 2.7 as of this
        # writing.
        commands_by_menu = {n: [] for n in menu_overrides.keys()}

        # We're placing a spacer before and after the context menu because
        # this is likely going into the existing "Shotgun" menu in RV, which
        # contains menu actions that will be listed before it.
        commands_by_menu[self.engine.default_menu_name] = [
            MenuGenerator.RV_MENU_SPACER,
            self._context_menu,
            MenuGenerator.RV_MENU_SPACER,
        ]

        # Organize the various commands into the appropriate RV menu
        # within our dictionary. If we find an override that came from
        # the config we put it into that RV menu's list of commands,
        # otherwise we fall back on the default menu defined by the
        # engine.
        #
        # Config setting structure:
        #
        # menu_overrides:
        #   SG Review:
        #     - {app_instance: tk-multi-importcut, name: Cut Import}
        #
        # Dictionary structure:
        #
        # commands_by_menu = {
        #     "Shotgun":[menu_item, ...],
        #     "SG Review":[menu_item, ...],
        # }
        for cmd in menu_commands:
            menu_item = cmd.define_menu_item()
            if cmd.get_type() == "context_menu":
                self._add_item_to_context_menu(menu_item)
            else:
                for menu_override, commands in menu_overrides.iteritems():
                    app_name = cmd.get_app_name()
                    if app_name in [c.get("app_instance") for c in commands if cmd.name == c.get("name")]:
                        commands_by_menu[menu_override].append(menu_item)
                    else:
                        commands_by_menu[self.engine.default_menu_name].append(menu_item)

        mode_menu_definition = []

        for menu_name, menu_items in commands_by_menu.iteritems():
            # If there are no commands to add to a specific menu, then
            # don't bother adding it to the menu definition.
            if not menu_items:
                continue
            mode_menu_definition.append((menu_name, menu_items))

        rv.commands.defineModeMenu(
            self.engine.toolkit_rv_mode_name,
            mode_menu_definition,
        )

    def destroy_menu(self):
        """
        Tears down the top-level menu in RV.
        """
        # This is a no-op right now. Because we allow engine commands
        # to both new and existing menus, we can't just zero out the
        # contents and be on our way.
        #
        # TODO: Menu destruction. Right now we'll end up with duplicate
        # menu items if the context ever changes.
        pass

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
        Gets the instance name of the parent app that registered this command.
        """
        if "app" in self.properties:
            return self.properties["app"].instance_name

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
            # Note that the None as the last argument pertains to a callback
            # RV can use to ask whether the menu item should be enabled/disabled,
            # and/or checked/unchecked. In our case we just want the default
            # behavior, which is active and unchecked.
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


        