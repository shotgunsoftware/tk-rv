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

import sgtk
import rv.qtutils
import rv.commands

from sgtk.platform import Engine, constants

class RVEngine(Engine):
    """
    Shotgun Toolkit engine for RV.
    """

    MAX_THREADS = 4

    #####################################################################################
    # Metrics

    def get_metrics_properties(self):
        """
        Returns a dictionary with properties to use when emitting a metric event for
        this engine.
        """

        properties = super(RVEngine, self).get_metrics_properties()
        properties["RV Debug Build"] = rv.commands.isDebug()
        properties["RV Release Variant"] = rv.commands.getReleaseVariant()

        return properties

    #####################################################################################
    # Properties

    @property
    def host_info(self):
        """
        Returns information about the application hosting this engine.
        """
        return {"name": "RV", "version": ".".join(rv.commands.getVersion())}

    @property
    def default_menu_name(self):
        """
        The name of the top-level menu created by the engine.

        :returns:   str
        """

        # XXX Set "SG Review" as the default top level menu, so that we don't
        # create another empty menu.  Eventually we'll want somewhere to store
        # "user apps" but we're not ready for that yet anyway.
        return "SG Review"

    @property
    def toolkit_rv_mode_name(self):
        """
        The name of the RV Mode that bootstrapped SGTK and started
        the engine.

        :returns:   str
        """
        return os.environ.get("TK_RV_MODE_NAME")

    @property
    def bg_task_manager(self):
        """
        An engine-level background task manager instance that can be
        shared across apps.

        :returns:   task_manager.BackgroundTaskManager
        """
        return self._bg_task_manager

    #####################################################################################
    # Engine Initialization and Destruction

    def pre_app_init(self):
        """
        Runs before apps have been initialized.
        """
        
        # Get Qt module regardless of version
        from sgtk.platform.qt import QtGui, QtCore

        # Here we're going to set the hyperlink text color to white
        # since the default is a dark blue that is pretty much unreadable
        # in a dark color environment like RV. It would be great if we
        # could style this in qss and only affect toolkit apps, but that's
        # no possible. As a result, we're modifying the QApplication-level
        # palette, which is also going to affect RV itself. This is generally
        # a BAD IDEA, but in this one case it is the best compromise solution
        # available.
        palette = QtGui.QApplication.palette()
        link_color = QtGui.QColor(255, 255, 255)
        palette.setColor(QtGui.QPalette.Link, link_color)
        palette.setColor(QtGui.QPalette.LinkVisited, link_color)
        palette.setColor(QtGui.QPalette.Button, QtGui.QColor(37, 38, 41))
        QtGui.QApplication.setPalette(palette)

        # We can't use import_framework here because the engine.py
        # wasn't imported via import_module itself. As a result, we
        # forgo the convenience and grab the framework ourselves and
        # import the submodules we need directly.
        shotgun_utils = self.frameworks["tk-framework-shotgunutils"]
        shotgun_globals = shotgun_utils.import_module("shotgun_globals")
        task_manager = shotgun_utils.import_module("task_manager")

        # We need a QObject to act as a parent for the task manager.
        # This will keep them and their threads from being garbage
        # collected prematurely by Qt.
        self.__task_parent = QtCore.QObject()

        # We will provide a task manager that apps can share.
        self._bg_task_manager = task_manager.BackgroundTaskManager(
            parent=self.__task_parent,
            start_processing=True,
            max_threads=RVEngine.MAX_THREADS,
        )

        shotgun_globals.register_bg_task_manager(self._bg_task_manager)

        # The "qss_watcher" setting causes us to monitor the engine's
        # style.qss file and re-apply it on the fly when it changes
        # on disk. This is very useful for development work,
        if self.get_setting("qss_watcher", False):
            self._qss_watcher = QtCore.QFileSystemWatcher(
                [os.path.join(self.disk_location, constants.BUNDLE_STYLESHEET_FILE)],
            )

            self._qss_watcher.fileChanged.connect(self.reload_qss)

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
            self._menu_generator.destroy_menu()

        self.bg_task_manager.shut_down()

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

    #####################################################################################
    # Styling

    def _create_dialog(self, *args, **kwargs):
        """
        Overrides and extends the default _create_dialog implementation
        from sgtk.platform.engine.Engine. Dialogs are created as is typical,
        and then have the tk-rv engine-specific style.qss file applies to
        them.
        """
        dialog = super(RVEngine, self)._create_dialog(*args, **kwargs)
        self._apply_external_styleshet(self, dialog)
        return dialog

    def reload_qss(self):
        """
        Causes the style.qss file that comes with the tk-rv engine to
        be re-applied to all dialogs that the engine has previously
        launched.
        """
        self.log_warning("Reloading engine QSS...")
        for dialog in self.created_qt_dialogs:
            self._apply_external_styleshet(self, dialog)
            dialog.update()


