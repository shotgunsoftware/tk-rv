from PySide.QtCore import QFile
from PySide import QtGui, QtCore

import types
import os
import math
import rv
import rv.qtutils
import tank

shotgun_view = tank.platform.import_framework("tk-framework-qtwidgets", "views")
shotgun_model = tank.platform.import_framework("tk-framework-shotgunutils", "shotgun_model")

from .version_list_delegate import RvVersionListDelegate
from .shot_info_delegate import RvShotInfoDelegate
from .tray_delegate import RvTrayDelegate

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
                        self.propName =  "%s.%s" % (fileSource[0], "tracking.info")
                        tl = rv.commands.getStringProperty(self.propName)
 
                        self._tracking_info= {}
                        
                        for i in range(0,len(tl)-1, 2):
                                self._tracking_info[tl[i]] = tl[i+1]
 
                        # make an entity
                        entity = {}
                        entity["type"] = "Version"
                        entity["id"] = int(self._tracking_info['id'])
                        if event.contents() == "viewGroup":
                                self.load_data(entity)
                                #self.version_activity_stream.ui.shot_info_widget.load_data_rv(self._tracking_info)

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

                        self._tracking_info= {}
                        
                        for i in range(0,len(tl)-1, 2):
                                self._tracking_info[tl[i]] = tl[i+1]
                        print self._tracking_info

                        # make an entity
                        entity = {}
                        entity["type"] = "Version"
                        entity["id"] = int(self._tracking_info['id'])
                        self.load_data(entity)
                        
                        #self.version_activity_stream.ui.shot_info_widget.load_data_rv(self._tracking_info)

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
                                if "infoStatus" not in event.contents():
                                        self._tracking_info= {}
                                        
                                        for i in range(0,len(tl)-1, 2):
                                                self._tracking_info[tl[i]] = tl[i+1]
                                        
                                        # make an entity
                                        entity = {}
                                        entity["type"] = "Version"
                                        entity["id"] = int(self._tracking_info['id'])
                                        
                                        self.load_data(entity)
                                        # self.version_activity_stream.ui.shot_info_widget.load_data_rv(self._tracking_info)

                                        s = self._tracking_info['shot']
                                        (s_id, s_name, s_type) = s.split('|')
                                        (n, shot_id) = s_id.split('_')
                
                                        # display VERSION info not parent shot info
                                        # shot_filters = [ ['id','is', entity['id']] ]
                                        # self.shot_info_model.load_data(entity_type="Version", filters=shot_filters)

                                        # version_filters = [ ['project','is', {'type':'Project','id':71}],
                                        #     ['entity','is',{'type':'Shot','id': int(shot_id) }] ]
                                        version_filters = [ ['entity','is',{'type':'Shot','id': int(shot_id) }] ]
                                        
                                        self.version_model.load_data(entity_type="Version", filters=version_filters)

                                        
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
                # print "group: %s fileSource: %s fileName: %s" % (group, fileSource, fileName)
                propName = "%s.%s" % (fileSource, "tracking.info")
                
                self.propName = propName
                self.group = group
                try:
                        tl = rv.commands.getStringProperty(propName)
                        self._tracking_info= {}
                        
                        for i in range(0,len(tl)-1, 2):
                                self._tracking_info[tl[i]] = tl[i+1]
                        
                        # make an entity
                        entity = {}
                        entity["type"] = "Version"
                        entity["id"] = int(self._tracking_info['id'])
                        
                        s = self._tracking_info['shot']
                        (s_id, s_name, s_type) = s.split('|')
                        (n, shot_id) = s_id.split('_')

                        self.load_data(entity)
                        
                        # shot_filters = [ ['id','is', int(shot_id)] ]
                        # self.shot_info_model.load_data(entity_type="Shot", filters=shot_filters)

                        #self.version_activity_stream.ui.shot_info_widget.load_data_rv(self._tracking_info)
                        version_filters = [ ['project','is', {'type':'Project','id':71}],
                            ['entity','is',{'type':'Shot','id': int(shot_id)}] ]
                        self.version_model.load_data(entity_type="Version", filters=version_filters)

                except Exception as e:
                        print "OH NO %r" % e

        def __init__(self):
                rv.rvtypes.MinorMode.__init__(self)
                self.note_dock = None
                self.tray_dock = None
                self.tab_widget = None

                self._tracking_info= {}

                self.init("RvActivityMode", None,
                        [ 
                                ("after-session-read", self.afterSessionRead, ""),
                                ("before-session-read", self.beforeSessionRead, ""),
                                # ("source-group-complete", self.sourceSetup, ""),
                                ("after-graph-view-change", self.viewChange, ""),
                                ("frame-changed", self.frameChanged, ""),
                                # ("graph-node-inputs-changed", self.inputsChanged, ""),
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
               shot_filters = [ ['id','is', entity['id']] ]
               self.shot_info_model.load_data(entity_type="Version", filters=shot_filters)
 
        # parent is note_dock here...
        def init_ui(self, note_dock, tray_dock):
                self.note_dock = note_dock
                self.tray_dock = tray_dock
 
                # setup Tab widget with notes and versions, then setup tray 
                self.tab_widget = QtGui.QTabWidget()

                self.tab_widget.setFocusPolicy(QtCore.Qt.NoFocus)
                self.tab_widget.setObjectName("tab_widget")
                
                activity_stream = tank.platform.import_framework("tk-framework-qtwidgets", "activity_stream")

                self.activity_tab_frame = QtGui.QWidget(self.note_dock)
                
                self.notes_container_frame = QtGui.QFrame(self.activity_tab_frame)
                self.cf_verticalLayout = QtGui.QVBoxLayout()
                self.cf_verticalLayout.setObjectName("cf_verticalLayout")
                self.notes_container_frame.setLayout(self.cf_verticalLayout)

                self.shot_info = QtGui.QListView()
                self.cf_verticalLayout.addWidget(self.shot_info)
                # self.version_activity_stream.ui.verticalLayout.addWidget(self.shot_info)
                
                self.shot_info_model = shotgun_model.SimpleShotgunModel(self.activity_tab_frame)
                self.shot_info.setModel(self.shot_info_model)

                self.shot_info_delegate = RvShotInfoDelegate(self.shot_info)
                self.shot_info.setItemDelegate(self.shot_info_delegate)

                self.shot_info.setVerticalScrollMode(QtGui.QAbstractItemView.ScrollPerPixel)
                self.shot_info.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
                self.shot_info.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
                self.shot_info.setHorizontalScrollMode(QtGui.QAbstractItemView.ScrollPerPixel)
                self.shot_info.setUniformItemSizes(True)
                self.shot_info.setObjectName("shot_info")

                from .shot_info_widget import ShotInfoWidget
                self.shot_info.setMinimumSize(ShotInfoWidget.calculate_size())
                si_size = ShotInfoWidget.calculate_size()
                self.shot_info.setMaximumSize(QtCore.QSize(si_size.width() + 10, si_size.height() + 10))
                
                shot_filters = [ ['id','is', 1161] ]
                self.shot_info_model.load_data(entity_type="Shot", filters=shot_filters, fields=["code", "link"])



                self.version_activity_stream = activity_stream.ActivityStreamWidget(self.notes_container_frame)
                self.cf_verticalLayout.addWidget(self.version_activity_stream)

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
                self.entity_version_view.setVerticalScrollMode(QtGui.QAbstractItemView.ScrollPerPixel)
                self.entity_version_view.setHorizontalScrollMode(QtGui.QAbstractItemView.ScrollPerPixel)
                self.entity_version_view.setUniformItemSizes(True)
                self.entity_version_view.setObjectName("entity_version_view")

                self.version_delegate  = RvVersionListDelegate(self.entity_version_view)
                self.version_model = shotgun_model.SimpleShotgunModel(self.entity_version_tab)

                # Tell the view to pull data from the model
                self.entity_version_view.setModel(self.version_model)
                self.entity_version_view.setItemDelegate(self.version_delegate)

                # load all assets from Shotgun 
                # REMOVE THIS LATER 
                # version_filters = [ 
                #                     ['project','is', {'type':'Project','id':65}],
                #                     ['entity','is',{'type':'Shot','id': 861}] 
                #                 ]
                # self.version_model.load_data(entity_type="Version", filters=version_filters)
                
                self.verticalLayout_3.addWidget(self.entity_version_view)

                self.version_activity_tab = QtGui.QWidget()
                self.version_activity_tab.setObjectName("version_activity_tab")
                
                self.version_activity_stream.setObjectName("version_activity_stream")
                
                self.tools_tab = QtGui.QWidget()
                self.tools_tab.setObjectName("tools_tab")

                self.tab_widget.addTab(self.notes_container_frame, "NOTES")                
                self.tab_widget.addTab(self.entity_version_tab, "VERSIONS")
                self.tab_widget.addTab(self.tools_tab, "TOOLS")

                self.note_dock.setWidget(self.tab_widget)

                # setup lower tray
                self.tray_list = QtGui.QListView(self.tray_dock)
                
                # self.tray_model = shotgun_model.SimpleShotgunModel(self.tray_list)
                from .tray_model import TrayModel
                self.tray_model = TrayModel(self.tray_list)

                self.tray_list.setModel(self.tray_model)

                self.tray_delegate = RvTrayDelegate(self.tray_list)
                self.tray_list.setItemDelegate(self.tray_delegate)

                # self.tray_list.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
                # self.tray_list.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
                self.tray_list.setHorizontalScrollMode(QtGui.QAbstractItemView.ScrollPerPixel)
                self.tray_list.setFlow(QtGui.QListView.LeftToRight)
                self.tray_list.setUniformItemSizes(True)
                self.tray_list.setMinimumSize(QtCore.QSize(900,150))
                self.tray_list.setObjectName("tray_list")

                from .tray_widget import TrayWidget
                #self.tray_list.setMinimumSize(TrayWidget.calculate_size())
                #si_size = TrayWidget.calculate_size()
                #self.tray_list.setMaximumSize(QtCore.QSize(si_size.width() + 10, si_size.height() + 10)) 

                tray_filters = [ ['sg_cut','is', {'type':'CustomEntity10', 'id': 8}] ]
                self.tray_model.load_data(entity_type="CustomEntity11", filters=tray_filters, fields=["sg_cut_in", "sg_cut_out", "sg_cut_order", "sg_version.Version.sg_path_to_frames", "sg_version.Version.id"])

                self.tray_list.clicked.connect(self.tray_clicked)
                
                #filters = [['id', 'is', 4]]
                #fields = ['code', 'sg_sort_order', 'versions.Version.code', 'versions.Version.user', 'versions.Version.entity']
                #order=[{'column':'sg_sort_order','direction':'asc'}]

        def on_item_changed(curr, prev):
            print curr, prev

        def tray_clicked(self, index):
            print "CLICK CLICK %r" % index
            sg_item = shotgun_model.get_sg_data(index)  
            print sg_item['sg_version.Version.id']
            entity = {}
            entity["type"] = "Version"
            entity["id"] = sg_item['sg_version.Version.id']
            
            # s = self._tracking_info['shot']
            # (s_id, s_name, s_type) = s.split('|')
            # (n, shot_id) = s_id.split('_')

            self.load_data(entity)
            
            # shot_filters = [ ['id','is', int(shot_id)] ]
            # self.shot_info_model.load_data(entity_type="Shot", filters=shot_filters)

            # version_filters = [ ['project','is', {'type':'Project','id':71}],
            #     ['entity','is',{'type':'Shot','id': int(shot_id)}] ]
            # self.version_model.load_data(entity_type="Version", filters=version_filters)
            


        def activate(self):
                rv.rvtypes.MinorMode.activate(self)

        def deactivate(self):
                rv.rvtypes.MinorMode.deactivate(self)



