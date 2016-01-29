# Copyright (c) 2015 Shotgun Software Inc.
# 
# CONFIDENTIAL AND PROPRIETARY
# 
# This work is provided "AS IS" and subject to the Shotgun Pipeline Toolkit 
# Source Code License included in this distribution package. See LICENSE.
# By accessing, using, copying or modifying this work you indicate your 
# agreement to the Shotgun Pipeline Toolkit Source Code License. All rights 
# not expressly granted therein are reserved by Shotgun Software In

"""
The OFFICIAL Toolkit engine for RV! 
Accept no substitutes.
"""

import os
import sys
import tank
import inspect
import logging

from tank.platform import Engine
from tank import TankError

# from rv import commands
import rv.qtutils
from PySide import QtCore

class RVEngine(Engine):

        def pre_app_init(self):
                self.log_debug("%r: Initializing..." % self)
                self.log_debug(os.environ.get("TANK_CONTEXT"))

                if self.context:
                        self.log_debug("TANK_CONTEXT is '%r'" % self.context)
                else:
                        self.log_debug("WARNING: No TANK_CONTEXT. USING big_buck_bunny again. Hey Rob where's my global context?")
                        self.context = self.context_from_path('/shotgunlocal/big_buck_bunny')

                # self.log_debug("INFO: TANK_CONTEXT is now '%r'" % self.context)

                self.toolkit_rv_mode_name = os.environ["TK_RV_MODE_NAME"]

                # we should be able to chuck this soon...
                if self.context.project is None:
                        self.log_debug("WARNING: tk-rv cant find a project. THIS MIGHT BE BAD")

                self._menu_name = "tk-rv"
                if self.get_setting("use_sgtk_as_menu_name", False):
                        self._menu_name = "SGTK"

                # the assumption here is that the default case has us presenting a Shotgun menu
                # and loading it with at least Cutz Support and maybe an expected Shotgun browser
                # or two. _ui_enabled turns the menu on. For shell access, setenv TK_RV_NO_UI NCC-1701
                # this is basically what tk-maya does so following along...
                # TODO how do i tell if im running via rvio?
                self._ui_enabled = True
                if os.environ.get("TK_RV_NO_UI"):
                        self._ui_enabled = False

                self._init_pyside()
                self._initialize_dark_look_and_feel()
 
                # unicode characters returned by the shotgun api need to be converted
                # to display correctly in all of the app windows
                from tank.platform.qt import QtCore
                # tell QT to interpret C strings as utf-8
                utf8 = QtCore.QTextCodec.codecForName("utf-8")
                QtCore.QTextCodec.setCodecForCStrings(utf8)
 
        def destroy_engine(self):
                self.log_debug("%r: Destroying tk-rv engine." % self)
                if self._ui_enabled:
                        self.log_debug("%r: Destroying Shotgun menu" % self)
                        self._menu_generator.destroy_menu()

        def has_ui(self):
                return self._ui_enabled
        
        def _init_pyside(self):
                # lifted from tk-maya        
                # first see if pyside is already present - in that case skip!
                try:
                        from PySide import QtGui
                except:
                        # fine, we don't expect pyside to be present just yet
                        self.log_debug("PySide not detected - it will be added to the setup now...")
                else:
                        # looks like pyside is already working! No need to do anything
                        self.log_debug("PySide detected - the existing version will be used.")
                        self.log_debug("%r" % QtGui)
                        return


                if sys.platform == "darwin":
                        # pyside_path = os.path.join(self.disk_location, "resources","pyside112_py26_qt471_mac", "python")
                        self.log_debug("Adding pyside to sys.path: %s" % pyside_path)
                        # sys.path.append(pyside_path)

                elif sys.platform == "win32" and self._maya_version.startswith("2013"):
                        # special 2013 version of pyside
                        # pyside_path = os.path.join(self.disk_location, "resources","pyside113_py26_qt471maya2013_win64", "python")
                        self.log_debug("Adding pyside to sys.path: %s" % pyside_path)
                        # sys.path.append(pyside_path)
                        # dll_path = os.path.join(self.disk_location, "resources","pyside113_py26_qt471maya2013_win64", "lib")
                        # path = os.environ.get("PATH", "")
                        # path += ";%s" % dll_path
                        # os.environ["PATH"] = path
            
                elif sys.platform == "win32":
                        # default windows version of pyside for 2011 and 2012
                        # pyside_path = os.path.join(self.disk_location, "resources","pyside111_py26_qt471_win64", "python")
                        self.log_debug("Adding pyside to sys.path: %s" % pyside_path)
                        # sys.path.append(pyside_path)
                        # dll_path = os.path.join(self.disk_location, "resources","pyside111_py26_qt471_win64", "lib")
                        # path = os.environ.get("PATH", "")
                        # path += ";%s" % dll_path
                        # os.environ["PATH"] = path

                elif sys.platform == "linux2":        
                        # pyside_path = os.path.join(self.disk_location, "resources","pyside112_py26_qt471_linux", "python")
                        self.log_debug("Adding pyside to sys.path: %s" % pyside_path)
                        # sys.path.append(pyside_path)

                else:
                        self.log_error("Unknown platform - cannot initialize PySide!")

                # now try to import it
                try:
                        from PySide import QtGui
                        from PySide import QtCore
                except Exception, e:
                        self.log_error("PySide could not be imported! Apps using pyside will not "
                                "operate correctly! Error reported: %s" % e)
                        self.log_debug('QtGui: %r' % QtGui)
                        self.log_debug('QtCore: %r' % QtCore)
                self.log_debug("QtCore loaded %r" % QtCore)


        def _get_dialog_parent(self):
                # self.log_debug('INFO: get_dialog_parent from QCoreApplication %r' % QtCore.QCoreApplication.instance())
                # self.log_debug('INFO: get_dialog_parent from QApplication %r' % QtGui.QApplication.instance() )
                return rv.qtutils.sessionWindow()

        def _get_gl_parent(self):
                return rv.qtutils.sessionGLView()

        def _get_top_toolbar(self):
                return rv.qtutils.sessionTopToolBar()

        def _get_bottom_toolbar(self):
                return rv.qtutils.sessionBottomToolBar()

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

        def post_app_init(self):
                # task_manager = tank.platform.import_framework("tk-framework-shotgunutils", "task_manager")
                # self._task_manager = task_manager.BackgroundTaskManager(parent=self._activity_stream,
                #                                                         start_processing=True,
                #                                                         max_threads=2)
                # shotgun_globals = tank.platform.import_framework("tk-framework-shotgunutils", "shotgun_globals")

                self.setup_menu()

        def setup_menu(self):
                if self._ui_enabled:
                        tk_rv = self.import_module("tk_rv")
                        self._menu_generator = tk_rv.MenuGenerator(self, self._menu_name)
                        self._menu_generator.create_menu()
                        # self._menu_generator._generate_cutz("")


