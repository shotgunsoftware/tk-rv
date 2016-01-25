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

def groupMemberOfType(node, memberType):
    for n in rv.commands.nodesInGroup(node):
        if rv.commands.nodeType(n) == memberType:
            return n
    return None

class RvActivityMode(rv.rvtypes.MinorMode):



        # def sourceSetup (self, event):
        #         print "&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&& sourceSetup"
        #         print event.contents()

        #         #
        #         #  event.reject() is done to allow other functions bound to
        #         #  this event to get a chance to modify the state as well. If
        #         #  its not rejected, the event will be eaten and no other call
        #         #  backs will occur.
        #         #

        #         event.reject()
 
        #         args         = event.contents().split(";;")
        #         group        = args[0]
        #         fileSource   = groupMemberOfType(group, "RVFileSource")
        #         imageSource  = groupMemberOfType(group, "RVImageSource")
        #         source       = fileSource if imageSource == None else imageSource
        #         typeName     = rv.commands.nodeType(source)
        #         fileNames    = rv.commands.getStringProperty("%s.media.movie" % source, 0, 1000)
        #         fileName     = fileNames[0]
        #         ext          = fileName.split('.')[-1].upper()
        #         mInfo        = rv.commands.sourceMediaInfo(source, None)
        #         print "group: %s fileSource: %s fileName: %s" % (group, fileSource, fileName)
        #         propName = "%s.%s" % (fileSource, "tracking.info")
                
        #         self.propName = propName
        #         self.group = group
        #         try:
        #                 tl = rv.commands.getStringProperty(propName)
        #                 print tl
        #                 #import ast
        #                 #tl = ast.literal_eval(tracking_str)
        #                 self._tracking_info= {}
                        
        #                 for i in range(0,len(tl)-1, 2):
        #                         self._tracking_info[tl[i]] = tl[i+1]
        #                 print self._tracking_info

        #                 # make an entity
        #                 entity = {}
        #                 entity["type"] = "Version"
        #                 entity["id"] = int(self._tracking_info['id'])
        #                 print entity
        #                 self.load_data(entity)
        #                 self.version_activity_stream.ui.shot_info_widget.load_data_rv(self._tracking_info)

        #         except Exception as e:
        #                 print "OH NO %r" % e

        def beforeSessionRead (self, event):
                print "################### beforeSessionRead"
                event.reject()

                self._readingSession = True

        def afterSessionRead (self, event):
                print "################### afterSessionRead"
                event.reject()

                self._readingSession = False

        def inputsChanged(self, event):
                pass
                print "################### inputsChanged %r" % event
                print event.contents()
                event.reject()
                try:
                        fileSource   = rv.commands.nodesOfType("#RVSource")
                        print fileSource
                        self.propName =  "%s.%s" % (fileSource[0], "tracking.info")
                        tl = rv.commands.getStringProperty(self.propName)
                        print tl

                        self._tracking_info= {}
                        
                        for i in range(0,len(tl)-1, 2):
                                self._tracking_info[tl[i]] = tl[i+1]
                        print self._tracking_info

                        # make an entity
                        entity = {}
                        entity["type"] = "Version"
                        entity["id"] = int(self._tracking_info['id'])
                        print entity
                        if event.contents() == "viewGroup":
                                self.load_data(entity)
                                self.version_activity_stream.ui.shot_info_widget.load_data_rv(self._tracking_info)

                except Exception as e:
                        print "OH NO %r" % e

        def viewChange(self, event):
                pass
                print "################### viewChange %r" % event
                print event.contents()
                event.reject()

        def frameChanged(self, event):
                print "################### frameChanged %r" % event
                print event.contents()
                event.reject()
                try:
                        tl = rv.commands.getStringProperty(self.propName)
                        print tl

                        self._tracking_info= {}
                        
                        for i in range(0,len(tl)-1, 2):
                                self._tracking_info[tl[i]] = tl[i+1]
                        print self._tracking_info

                        # make an entity
                        entity = {}
                        entity["type"] = "Version"
                        entity["id"] = int(self._tracking_info['id'])
                        print entity
                        self.load_data(entity)
                        self.version_activity_stream.ui.shot_info_widget.load_data_rv(self._tracking_info)

                except Exception as e:
                        print "OH NO %r" % e

        def sourcePath(self, event):
                pass
                print "################### sourcePath %r" % event
                print event.contents()
                event.reject()

        def graphStateChange(self, event):
                pass
                print "################### graphStateChange %r" % event
                print event.contents()
                event.reject()
                if "tracking.info" in event.contents():
                        try:
                                tl = rv.commands.getStringProperty(event.contents())
                                print tl
                                if "infoStatus" not in event.contents():
                                        self._tracking_info= {}
                                        
                                        for i in range(0,len(tl)-1, 2):
                                                self._tracking_info[tl[i]] = tl[i+1]
                                        print self._tracking_info

                                        # make an entity
                                        entity = {}
                                        entity["type"] = "Version"
                                        entity["id"] = int(self._tracking_info['id'])
                                        print entity
                                        self.load_data(entity)
                                        self.version_activity_stream.ui.shot_info_widget.load_data_rv(self._tracking_info)
                                        
                        except Exception as e:
                                print "TRACKING ERROR: %r" % e

        def sourceGroupComplete(self, event):
                print "################### sourceGroupComplete %r" % event
                print event.contents()
                event.reject()
                args         = event.contents().split(";;")
                group        = args[0]
                fileSource   = groupMemberOfType(group, "RVFileSource")
                imageSource  = groupMemberOfType(group, "RVImageSource")
                source       = fileSource if imageSource == None else imageSource
                typeName     = rv.commands.nodeType(source)
                fileNames    = rv.commands.getStringProperty("%s.media.movie" % source, 0, 1000)
                fileName     = fileNames[0]
                ext          = fileName.split('.')[-1].upper()
                mInfo        = rv.commands.sourceMediaInfo(source, None)
                print "group: %s fileSource: %s fileName: %s" % (group, fileSource, fileName)
                propName = "%s.%s" % (fileSource, "tracking.info")
                
                self.propName = propName
                self.group = group
                try:
                        tl = rv.commands.getStringProperty(propName)
                        print tl
                        #import ast
                        #tl = ast.literal_eval(tracking_str)
                        self._tracking_info= {}
                        
                        for i in range(0,len(tl)-1, 2):
                                self._tracking_info[tl[i]] = tl[i+1]
                        print self._tracking_info

                        # make an entity
                        entity = {}
                        entity["type"] = "Version"
                        entity["id"] = int(self._tracking_info['id'])
                        print entity
                        self.load_data(entity)
                        self.version_activity_stream.ui.shot_info_widget.load_data_rv(self._tracking_info)

                except Exception as e:
                        print "OH NO %r" % e

        def __init__(self):
                rv.rvtypes.MinorMode.__init__(self)
                self.parent = None
                self.tab_widget = None

                self._tracking_info= {}

                self.init("RvActivityMode", None,
                        [ 
                                ("after-session-read", self.afterSessionRead, ""),
                                ("before-session-read", self.beforeSessionRead, ""),
                                # ("source-group-complete", self.sourceSetup, ""),
                                ("after-graph-view-change", self.viewChange, ""),
                                ("frame-changed", self.frameChanged, ""),
                                ("graph-node-inputs-changed", self.inputsChanged, ""),
                                ("incoming-source-path", self.sourcePath, ""),
                                ("source-group-complete", self.sourceGroupComplete, ""),
                                ("graph-state-change", self.graphStateChange, "")
                        ],
                        None,
                        None);


        def load_data(self, entity):
                # our session property is called tracking
                #tracking_str = rv.commands.getStringProperty('sourceGroup000001_source.tracking.info ')
                #print tracking_str
               print "ACTIVITY NODE @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@"
               self.version_activity_stream.load_data(entity)
 
        def init_ui(self, parent):
                self.parent = parent
                self.tab_widget = QtGui.QTabWidget()

                self.tab_widget.setFocusPolicy(QtCore.Qt.NoFocus)
                self.tab_widget.setObjectName("tab_widget")
                
                activity_stream = tank.platform.import_framework("tk-framework-qtwidgets", "activity_stream")

                self.activity_tab_frame = QtGui.QWidget(self.parent)
                self.version_activity_stream = activity_stream.ActivityStreamWidget(self.activity_tab_frame)
                

                self.tab_widget.setStyleSheet("QWidget { font-family: Proxima Nova; font-size: 16px; background: rgb(36,38,41); color: rgb(126,127,129); border-color: rgb(36,38,41);}\
                    QTabWidget::tab-bar { alignment: center; border: 2px solid rgb(236,38,41); } \
                    QTabBar::tab { border: 2px solid rgb(36,38,41); alignment: center; background: rgb(36,38,41); margin: 4px; color: rgb(126,127,129); }\
                    QTabBar::tab:selected { color: rgb(40,136,175)} \
                    QTabWidget::pane { border-top: 2px solid rgb(66,67,69); }")


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
                # REMOVE THIS LATER 
                version_filters = [ ['project','is', {'type':'Project','id':65}],
                                ['entity','is',{'type':'Shot','id': 861}] ]
                self.version_model.load_data(entity_type="Version", filters=version_filters)
                
                self.verticalLayout_3.addWidget(self.entity_version_view)

                self.version_activity_tab = QtGui.QWidget()
                self.version_activity_tab.setObjectName("version_activity_tab")
                
                self.version_activity_stream.setObjectName("version_activity_stream")
                
                # self.tools_tab = QtGui.QWidget()
                # self.tools_tab.setObjectName("tools_tab")
                
                self.tab_widget.addTab(self.version_activity_stream, "NOTES")                
                self.tab_widget.addTab(self.entity_version_tab, "VERSIONS")
                # self.tab_widget.addTab(self.tools_tab, "TOOLS")

                # note_icon = QtGui.QIcon(':/resources/review_app_notes@2x.png')
                # print "NOTE %r" % note_icon
                # self.tab_widget.setTabIcon(1, note_icon)
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
        # print "NEARG"
        # print(str(sg_item))
        # print "WID: %r" % widget

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


