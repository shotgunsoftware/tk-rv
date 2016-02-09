# Copyright (c) 2016 Shotgun Software Inc.
# 
# CONFIDENTIAL AND PROPRIETARY
# 
# This work is provided "AS IS" and subject to the Shotgun Pipeline Toolkit 
# Source Code License included in this distribution package. See LICENSE.
# By accessing, using, copying or modifying this work you indicate your 
# agreement to the Shotgun Pipeline Toolkit Source Code License. All rights 
# not expressly granted therein are reserved by Shotgun Software Inc.

"""
The OFFICIAL Toolkit engine for RV! 
Accept no substitutes.
"""

import os
import sys
import tank

from tank.platform import Engine
from tank import TankError

import rv.qtutils
from PySide import QtCore

class RVEngine(Engine):
    #####################################################################################
    # Properties

    @property
    def toolkit_rv_mode_name(self):
        return os.environ.get("TK_RV_MODE_NAME")

    @property
    def menu_name(self):
        if self.get_setting("use_sgtk_as_menu_name"):
            return "SGTK"
        else:
            return "tk-rv"

    #####################################################################################
    # Engine Initialization and Destruction

    def pre_app_init(self):
        self.log_debug("%r: Initializing..." % self)
        self.log_debug(os.environ.get("TANK_CONTEXT"))

        # The assumption here is that the default case has us presenting a
        # Shotgun menu and loading it with at least Cutz Support and maybe
        # an expected Shotgun browser or two. _ui_enabled turns the menu on.
        # For shell access, setenv TK_RV_NO_UI NCC-1701 this is basically what
        # tk-maya does so following along.
        self._ui_enabled = os.environ.get("TK_RV_NO_UI") or True

        # Unicode characters returned by the shotgun api need to be converted
        # to display correctly in all of the app windows. Tell Qt to interpret
        # C strings as utf-8.
        utf8 = QtCore.QTextCodec.codecForName("utf-8")
        QtCore.QTextCodec.setCodecForCStrings(utf8)

    def post_app_init(self):
        if self._ui_enabled:
            tk_rv = self.import_module("tk_rv")
            self._menu_generator = tk_rv.MenuGenerator(self)
            self._menu_generator.create_menu()

    def destroy_engine(self):
        self.log_debug("%r: Destroying tk-rv engine." % self)

        if self._ui_enabled:
            self.log_debug("%r: Destroying Shotgun menu" % self)
            self._menu_generator.destroy_menu()

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
        return self._ui_enabled

    def get_dialog_parent(self):
        return rv.qtutils.sessionWindow()

    def get_gl_parent(self):
        return rv.qtutils.sessionGLView()

    def get_top_toolbar(self):
        return rv.qtutils.sessionTopToolBar()

    def get_bottom_toolbar(self):
        return rv.qtutils.sessionBottomToolBar()


