# Copyright (c) 2016 Shotgun Software Inc.
# 
# CONFIDENTIAL AND PROPRIETARY
# 
# This work is provided "AS IS" and subject to the Shotgun Pipeline Toolkit 
# Source Code License included in this distribution package. See LICENSE.
# By accessing, using, copying or modifying this work you indicate your 
# agreement to the Shotgun Pipeline Toolkit Source Code License. All rights 
# not expressly granted therein are reserved by Shotgun Software Inc.

class AppCommand(object):
    """
    Wraps around a single command that you get from engine.commands
    """

    def __init__(self, name, command_dict):
        self.name = name
        self.properties = command_dict["properties"]
        self.callback = command_dict["callback"]
        self.favourite = False

    def get_app_name(self):
        """
        Returns the name of the app that this command belongs to
        """
        if "app" in self.properties:
            return self.properties["app"].display_name
        return None

    def get_app_instance_name(self):
        """
        Returns the name of the app instance, as defined in the environment.
        Returns None if not found.
        """
        if "app" not in self.properties:
            return None

        app_instance = self.properties["app"]
        engine = app_instance.engine
        for (app_instance_name, app_instance_obj) in engine.apps.items():
            if app_instance_obj == app_instance:
                return app_instance_name

        return None

    def get_documentation_url_str(self):
        """
        Returns the documentation as a str
        """
        if "app" in self.properties:
            app = self.properties["app"]
            doc_url = app.documentation_url
            # deal with nuke's inability to handle unicode. #fail
            if doc_url.__class__ == unicode:
                doc_url = unicodedata.normalize('NFKD', doc_url).encode('ascii', 'ignore')
            return doc_url

        return None

    def get_type(self):
        """
        returns the command type. Returns node, custom_pane or default
        """
        return self.properties.get("type", "default")

    def define_menu_item(self):
        """
        Adds an app command to the menu item
        """

        hotkey = self.properties.get("hotkey")
        if hotkey:
            menu_item = (self.name, self.menu_item_callback, hotkey, None)
        else:
            menu_item = (self.name, self.menu_item_callback, None, None)

        return menu_item

    def menu_item_callback(self, event):
        self.callback()
