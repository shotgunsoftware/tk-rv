from PySide import QtGui, QtCore

import types
import os
import math
import rv
import rv.qtutils
import tank

from .tray_widget import TrayWidget


shotgun_view = tank.platform.import_framework("tk-framework-qtwidgets", "views")
shotgun_model = tank.platform.import_framework("tk-framework-shotgunutils", "shotgun_model")



class RvTrayDelegate(shotgun_view.WidgetDelegate):

        def __init__(self, view):
                    #from tank.platform.qt import QtCore, QtGui
                    #ListItemWidget.resize(366, 109)
                    self.tray_view = view
                    shotgun_view.WidgetDelegate.__init__(self, view)

        def _create_widget(self, parent):
                    """
                    Returns the widget to be used when creating items
                    """
                    return TrayWidget(parent)

        def _on_before_paint(self, widget, model_index, style_options):
                    """
                    Called when a cell is being painted.
                    """   
                    # get the shotgun query data for this model item     
                    sg_item = shotgun_model.get_sg_data(model_index)   

                    # ptf = sg_item.get('sg_version.Version.sg_path_to_frames')
                    # rv.commands.addSource(ptf)
                    # if widget.take_ptf == None:
                    #     widget.take_ptf = ptf
                    #     self.tray_view.ptfs.append(ptf)
                    #     print sg_item
                    # print "WIDGET %r" % widget
                    # ShotgunModel.SG_ASSOCIATED_FIELD_ROLE
                    # extract the standard icon associated with the item
                    icon = model_index.data(QtCore.Qt.DecorationRole)
                    thumb = icon.pixmap(100)

                    #widget.thumbnail.setMaximumSize(QtCore.QSize(750, 750))
                    widget.set_thumbnail(thumb)
                    # widget.ui.thumbnail.setScaledContents(False)
                    
                    
                    # fill the content of the widget with the data of the loaded Shotgun
                    # code_str = sg_item.get("code")
                    # type_str = sg_item.get("type")
                    # id_str = sg_item.get("id")

                    # header_str = "%s" % (code_str)
                    # body_str = "%s %s" % (type_str, id_str)
                    # widget.set_text(header_str, body_str)

        def _on_before_selection(self, widget, model_index, style_options):
                    """
                    Called when a cell is being selected.
                    """
                    # do std drawing first
                    print "_on_before_selection"
                    self._on_before_paint(widget, model_index, style_options)        
                    widget.set_selected(True)        

        def sizeHint(self, style_options, model_index):
                    """
                    Base the size on the icon size property of the view
                    """
                    return TrayWidget.calculate_size()
                    #return QtCore.QSize(150,100)


