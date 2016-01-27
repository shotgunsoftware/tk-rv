from PySide import QtGui, QtCore

import types
import os
import math
import rv
import rv.qtutils
import tank

from .list_widget import ListWidget


shotgun_view = tank.platform.import_framework("tk-framework-qtwidgets", "views")
shotgun_model = tank.platform.import_framework("tk-framework-shotgunutils", "shotgun_model")



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
                    code_str = sg_item.get("code")
                    type_str = sg_item.get("type")
                    id_str = sg_item.get("id")
                    header_str = "<br><b>%s</b>" % (code_str)
                    body_str = "<b>%s</b> &mdash; %s" % (type_str, id_str)
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


