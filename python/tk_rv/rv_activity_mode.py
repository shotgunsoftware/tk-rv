from PySide.QtCore import QFile
from PySide import QtGui, QtCore
# from PySide.QtGui import QDoubleSpinBox, QDial, QCheckBox
# from PySide.QtUiTools import QUiLoader

import types
import os
import math
import rv
import rv.qtutils
import tank

shotgun_view = tank.platform.import_framework("tk-framework-qtwidgets", "views")
shotgun_model = tank.platform.import_framework("tk-framework-shotgunutils", "shotgun_model")

from .list_widget import ListWidget


class RvActivityMode(rv.rvtypes.MinorMode):

        def __init__(self):
                rv.rvtypes.MinorMode.__init__(self)
                self.parent = None
                self.tab_widget = None

        def load_data(self, entity):
                self.version_activity_stream.load_data(entity)

        def init_ui(self, parent):
                self.parent = parent
                self.tab_widget = QtGui.QTabWidget()

                self.tab_widget.setFocusPolicy(QtCore.Qt.NoFocus)
                self.tab_widget.setObjectName("tab_widget")

                # shotgun_model = tank.platform.import_framework("tk-framework-shotgunutils", "shotgun_model")
                
                activity_stream = tank.platform.import_framework("tk-framework-qtwidgets", "activity_stream")
                self.version_activity_stream = activity_stream.ActivityStreamWidget(self.parent)
                
                task_manager = tank.platform.import_framework("tk-framework-shotgunutils", "task_manager")
                self._task_manager = task_manager.BackgroundTaskManager(parent=self.version_activity_stream,
                                                                        start_processing=True,
                                                                        max_threads=2)
                
                shotgun_globals = tank.platform.import_framework("tk-framework-shotgunutils", "shotgun_globals")
                shotgun_globals.register_bg_task_manager(self._task_manager)
                
                self.version_activity_stream.set_bg_task_manager(self._task_manager)
                

                self.entity_version_tab = QtGui.QWidget()
                self.entity_version_tab.setObjectName("entity_version_tab")
                
                self.verticalLayout_3 = QtGui.QVBoxLayout(self.entity_version_tab)
                self.verticalLayout_3.setContentsMargins(0, 0, 0, 0)
                self.verticalLayout_3.setObjectName("verticalLayout_3")
                
                self.entity_version_view = QtGui.QListView(self.entity_version_tab)
                # self._sg_tk_test = shotgun_view.ListWidget(parent_widget)
                self.version_delegate  = RvVersionListDelegate(self.entity_version_view)
                # Set up our data backend
                self.version_model = shotgun_model.SimpleShotgunModel(self.entity_version_tab)


                self.entity_version_view.setVerticalScrollMode(QtGui.QAbstractItemView.ScrollPerPixel)
                self.entity_version_view.setHorizontalScrollMode(QtGui.QAbstractItemView.ScrollPerPixel)
                self.entity_version_view.setUniformItemSizes(True)
                self.entity_version_view.setObjectName("entity_version_view")




                # Tell the view to pull data from the model
                self.entity_version_view.setModel(self.version_model)
                self.entity_version_view.setItemDelegate(self.version_delegate)
                # load all assets from Shotgun
                version_filters = [ ['project','is', {'type':'Project','id':65}],
                                ['entity','is',{'type':'Shot','id': 861}] ]
                self.version_model.load_data(entity_type="Version", filters=version_filters)
                # self.entity_version_view.show()

                
                self.verticalLayout_3.addWidget(self.entity_version_view)

                self.version_activity_tab = QtGui.QWidget()
                self.version_activity_tab.setObjectName("version_activity_tab")
                
                #self.verticalLayout_20 = QtGui.QVBoxLayout(self.version_activity_tab)
                #self.verticalLayout_20.setContentsMargins(10, 0, 0, 0)
                #self.verticalLayout_20.setObjectName("verticalLayout_20")
                
                #self.version_activity_stream = ActivityStreamWidget(self.version_activity_tab)
                self.version_activity_stream.setObjectName("version_activity_stream")
                
                #self.verticalLayout_20.addWidget(self.version_activity_stream)
                
                self.tab_widget.addTab(self.version_activity_stream, "Activity")                
                self.tab_widget.addTab(self.entity_version_tab, "Versions")

                self.parent.setWidget(self.tab_widget)




        def activate(self):
                rv.rvtypes.MinorMode.activate(self)
                #self.dialog.show()

        def deactivate(self):
                rv.rvtypes.MinorMode.deactivate(self)
                #self.dialog.hide()

class RvVersionListDelegate(shotgun_view.WidgetDelegate):

    def __init__(self, view):
        #from tank.platform.qt import QtCore, QtGui
        #ListItemWidget.resize(366, 109)
        shotgun_view.WidgetDelegate.__init__(self, view)

    def _create_widget(self, parent):
        """
        Returns the widget to be used when creating items
        """
        return ListWidget(parent)
        #return QtGui.QListView(parent)

    def _on_before_paint(self, widget, model_index, style_options):
        """
        Called when a cell is being painted.
        """   

        # extract the standard icon associated with the item
        icon = model_index.data(QtCore.Qt.DecorationRole)
        thumb = icon.pixmap(100)

        #widget.thumbnail.setMaximumSize(QtCore.QSize(750, 750))
        widget.set_thumbnail(thumb)
        # widget.ui.thumbnail.setScaledContents(False)
        
        # get the shotgun query data for this model item     
        sg_item = shotgun_model.get_sg_data(model_index)   

        # fill the content of the widget with the data of the loaded Shotgun
        # item
        print "NEARG"
        print(str(sg_item))
        print "WID: %r" % widget

        code_str = sg_item.get("code")
        type_str = sg_item.get("type")
        id_str = sg_item.get("id")
        header_str = "<br><b>%s</b>" % (code_str)
        body_str = "<b>%s</b> &mdash; %s" % (type_str, id_str)
        # print header_str
        widget.set_text(header_str, body_str)

    def _on_before_selection(self, widget, model_index, style_options):
        """
        Called when a cell is being selected.
        """
        # do std drawing first
        self._on_before_paint(widget, model_index, style_options)        
        widget.set_selected(True)        

    def sizeHint(self, style_options, model_index):
        """
        Base the size on the icon size property of the view
        """
        #return shotgun_view.ListWidget.calculate_size()
        return QtCore.QSize(150,100)


