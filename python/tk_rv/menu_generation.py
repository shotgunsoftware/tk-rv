"""
Menu handling for RV

"""

import tank
import sys
import os
import unicodedata

import rv.commands
import rv.qtutils

from tank.platform.qt import QtGui, QtCore

class MenuGenerator(object):

        def __init__(self, engine, menu_name):
                self._engine = engine
                self._menu_name = menu_name

                # kinda bogus stuff i made
                # self._rv_pyside_test = None
                # self._sg_tk_test = None
                self.rvSessionQObject = rv.qtutils.sessionWindow()
                # self.server_thread = None

        # does this get called more than once?
        def create_menu(self, *args):
                self._engine.log_debug("INFO: create_menu.")

                self._menu_handle = []

                sgtk_menu = [(self._menu_name, [("_", None)])]
                rv.commands.defineModeMenu(self._engine.toolkit_rv_mode_name, sgtk_menu)

                self._context_menu = self._add_context_menu()
                self._menu_handle.append(self._context_menu)

                separator_item = ("_", None)
                self._menu_handle.append(separator_item)

                menu_items = []
                # for AppCommand
                # is this the preferred way?
                tk_rv = self._engine.import_module("tk_rv")
                self._engine.log_debug("create_menu tk_rv imported.")

                for (cmd_name, cmd_details) in self._engine.commands.items():
                        menu_items.append(tk_rv.AppCommand(cmd_name, cmd_details))

                menu_items.sort(key=lambda x: x.name)

                # add favourites to the menu
                for fav in self._engine.get_setting("menu_favourites", []):
                        app_instance_name = fav["app_instance"]
                        menu_name = fav["name"]
                        for cmd in menu_items:
                                if cmd.get_app_instance_name() == app_instance_name and cmd.name == menu_name:
                                        menu_item = cmd.define_menu_item()
                                        self._menu_handle.append(menu_item)
                                        cmd.favourite = True

                # add separator
                self._menu_handle.append(separator_item)
                self._engine.log_debug("create_menu seperator")

                # separate menu items out into various sections
                commands_by_app = {}
                for cmd in menu_items:
                        if cmd.get_type() == "context_menu":
                                #menu_item = cmd.define_menu_item()
                                #self._context_menu[1].append(menu_item)
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
                sgtk_menu = [(self._menu_name, self._menu_handle)]
                rv.commands.defineModeMenu(self._engine.toolkit_rv_mode_name, sgtk_menu)
                self._engine.log_debug("create_menu done.")


        def destroy_menu(self):
                #self._rv_pyside_test.deactivate()
                #self._rv_pyside_test.close()

                self._engine.log_debug("destroy_menu: %r." % self)

                #self._engine._on_dialog_closed(self._sg_tk_test)
                self._engine.__qt_widget_trash.append(self._sg_tk_test)

                sgtk_menu = [("", [("_", None)])]
                rv.commands.defineModeMenu(self._engine.toolkit_rv_mode_name, sgtk_menu)



        ##########################################################################################
        # context menu and UI

        def _add_context_menu(self):
                ctx = self._engine.context
                ctx_name = str(ctx)
                # cutz_item = ("Cutz", self._cutz, None, None)
                # env_item = ("Env Info", self._env_info, None, None)
                note_item = ("Note Info", self._note_pad, None, None)
 
                # jump_shotgun_item = ("Jump To Shotgun", self._jump_to_sg, None, None)
                # jump_file_sys_item = ("Jump To File System", self._jump_to_fs, None, None)
 
                separator_item = ("_", None, None, None)
 
                ctx_menu = (ctx_name, [note_item, separator_item])
                return ctx_menu

        def _note_pad(self, event):

                from PySide import QtGui
                parent_widget = rv.qtutils.sessionWindow() #self._engine._get_dialog_parent()
                self.dock_thing = QtGui.QDockWidget("CutZ", parent_widget)
                
                parent_widget.setStyleSheet("QWidget { font-family: Proxima Nova; background: rgb(36,38,41); color: rgb(126,127,129); border-color: rgb(36,38,41);}")
                self.dock_thing.setStyleSheet("QWidget { font-family: Proxima Nova; background: rgb(36,38,41); color: rgb(126,127,129);} \
                        QDockWidget::title { background: rgb(36,38,41); color: rgb(126,127,129); padding: 8px; border: 0px;}")
                
                self.dock_thing.setAllowedAreas(QtCore.Qt.LeftDockWidgetArea | QtCore.Qt.RightDockWidgetArea)
                self._engine._get_top_toolbar().addAction(self.dock_thing.toggleViewAction())
                
                tk_rv = self._engine.import_module("tk_rv")
                tk_rv_cuts = self._engine.import_module("tk_rv_cuts")

                self.rv_activity_stream = tk_rv_cuts.RvActivityMode()
                self.rv_activity_stream.init_ui(self.dock_thing)
                rv.commands.activateMode("RvActivityMode")
                #self.dock_thing.setMinimumSize(320,500)
                # self.dock_thing.resize(600,600)
                parent_widget.addDockWidget(QtCore.Qt.RightDockWidgetArea, self.dock_thing)
                self._env_info(event)



        def _env_info(self, event):

                self._engine.log_info("TANK_CONTEXT: %s" % os.environ.get("TANK_CONTEXT"))
                from PySide import QtGui
                self._engine.log_info('QtGui: %r' % QtGui)
                from PySide import QtCore
                self._engine.log_info('QtCore: %r' % QtCore)
                self.rv_activity_stream.load_data( { "type": "Version", "id": 41})
                # self.rv_activity_stream.load_data( { "type": "Shot", "id": 861})


        def _cutz(self, event):
                pass


                
shotgun_model = tank.platform.import_framework("tk-framework-shotgunutils", "shotgun_model")
shotgun_view = tank.platform.import_framework("tk-framework-qtwidgets", "views")


class ExampleDelegate(shotgun_view.WidgetDelegate):
        """
        Shows an example how to use a shotgun_view.ListWidget in a std view.
        """

        def __init__(self, view):
                #from tank.platform.qt import QtCore, QtGui
                #ListItemWidget.resize(366, 109)
                shotgun_view.WidgetDelegate.__init__(self, view)

        def _create_widget(self, parent):
                # return shotgun_view.ListWidget(parent)
                return shotgun_view.ListWidget(parent)

        def _on_before_paint(self, widget, model_index, style_options):
                # extract the standard icon associated with the item
                icon = model_index.data(QtCore.Qt.DecorationRole)
                thumb = icon.pixmap(100)

                #widget.thumbnail.setMaximumSize(QtCore.QSize(750, 750))
                widget.set_thumbnail(thumb)
                widget.ui.thumbnail.setScaledContents(False)
                
                # get the shotgun query data for this model item     
                sg_item = shotgun_model.get_sg_data(model_index)   

                # fill the content of the widget with the data of the loaded Shotgun
                # item
                # print(str(sg_item))

                code_str = sg_item.get("code")
                type_str = sg_item.get("type")
                id_str = sg_item.get("id")
                header_str = "<br><b>%s</b>" % (code_str)
                body_str = "<b>%s</b> &mdash; %s" % (type_str, id_str)
                widget.set_text(header_str, body_str)

        def _on_before_selection(self, widget, model_index, style_options):
                # do std drawing first
                self._on_before_paint(widget, model_index, style_options)        
                widget.set_selected(True)        

        def sizeHint(self, style_options, model_index):
                """
                Base the size on the icon size property of the view
                """
                #return shotgun_view.ListWidget.calculate_size()

                return QtCore.QSize(150,100)
