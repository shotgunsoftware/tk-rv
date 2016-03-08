# Copyright (c) 2016 Shotgun Software Inc.
# 
# CONFIDENTIAL AND PROPRIETARY
# 
# This work is provided "AS IS" and subject to the Shotgun Pipeline Toolkit 
# Source Code License included in this distribution package. See LICENSE.
# By accessing, using, copying or modifying this work you indicate your 
# agreement to the Shotgun Pipeline Toolkit Source Code License. All rights 
# not expressly granted therein are reserved by Shotgun Software Inc.

import os
import sys

import tank
import rv.qtutils

from tank.platform import Engine
# from tank.platform.qt import QtGui, QtCore

class RVEngine(Engine):
    """
    Shotgun Toolkit engine for RV.
    """

    #####################################################################################
    # Properties

    @property
    def context_change_allowed(self):
        """
        Specifies that on-the-fly context changes are supported.
        """
        return True

    @property
    def toolkit_rv_mode_name(self):
        """
        The name of the RV Mode that bootstrapped SGTK and started
        the engine.
        """
        return os.environ.get("TK_RV_MODE_NAME")

    @property
    def menu_name(self):
        """
        The name of the top-level menu created by the engine.
        """
        return "SG Review"

    #####################################################################################
    # Engine Initialization and Destruction

    def pre_app_init(self):
        """
        Runs before apps have been initialized.
        """
        # The assumption here is that the default case has us presenting a
        # Shotgun menu and loading it with at least Cutz Support and maybe
        # an expected Shotgun browser or two. _ui_enabled turns the menu on.
        # For shell access, setenv TK_RV_NO_UI NCC-1701 this is basically what
        # tk-maya does so following along.
        self._ui_enabled = os.environ.get("TK_RV_NO_UI") or True

        # Unicode characters returned by the shotgun api need to be converted
        # to display correctly in all of the app windows. Tell Qt to interpret
        # C strings as utf-8.
        # utf8 = QtCore.QTextCodec.codecForName("utf-8")
        # QtCore.QTextCodec.setCodecForCStrings(utf8)

    def post_app_init(self):
        """
        Runs after all apps have been initialized. If running in a GUI
        session of RV, the "SG Review" menu will be created and populated
        with any app commands that have been registered with the engine.
        """
        if self._ui_enabled:
            tk_rv = self.import_module("tk_rv")
            self._menu_generator = tk_rv.MenuGenerator(self)
            self._menu_generator.create_menu()

    def destroy_engine(self):
        """
        Tears down the engine and any menu items it has created.
        """
        self.log_debug("%r: Destroying tk-rv engine." % self)

        if self._ui_enabled:
            self.log_debug("%r: Destroying %s menu" % (self, self.menu_name))
            self._menu_generator.destroy_menu()

    def post_context_change(self, old_context, new_context):
        """
        Run after any on-the-fly context changes. This will trigger a
        rebuild of the top-level menu created by the engine when it was
        initialized.

        :param old_context: The previously-active context.
        :param new_context: The context that was switched to.
        """
        if not self._ui_enabled:
            return

        self._menu_generator.destroy_menu()
        self._menu_generator.create_menu()

    #####################################################################################
    # Logging

    def log_debug(self, msg):
        if self.get_setting("debug_logging", True):
            msg = "DEBUG: tk-rv - %s" % msg
            print >> sys.stderr, msg

    def log_info(self, msg):
        msg = "INFO: tk-rv - %s" % msg
        print >> sys.stderr, msg

    def log_warning(self, msg):
        msg = "WARNING: tk-rv - %s" % msg
        print >> sys.stderr, msg

    def log_error(self, msg):
        msg = "ERROR: tk-rv - %s" % msg
        print >> sys.stderr, msg

    #####################################################################################
    # General Utilities

    def has_ui(self):
        """
        Whether RV is running in UI mode or not.
        """
        return self._ui_enabled

    def get_dialog_parent(self):
        """
        The parent widget to use when creating top-level widgets for use
        in RV.
        """
        return rv.qtutils.sessionWindow()

    def get_gl_parent(self):
        """
        The RV session's GLView object.
        """
        return rv.qtutils.sessionGLView()

    def get_top_toolbar(self):
        """
        RV's top toolbar widget.
        """
        return rv.qtutils.sessionTopToolBar()

    def get_bottom_toolbar(self):
        """
        RV's bottom toolbar widget.
        """
        return rv.qtutils.sessionBottomToolBar()


