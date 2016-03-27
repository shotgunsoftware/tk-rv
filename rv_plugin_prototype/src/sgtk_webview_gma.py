
import sys

from PySide import QtCore, QtGui, QtWebKit

from rv import commands as rvc
from rv import extra_commands as rve
from rv import rvtypes as rvt
from rv import qtutils as rvqt

from shiboken import getCppPointer

class pyGMAWindow :

    def __init__(self, serverURL) :
        sys.stderr.write("************************************************** pGMAWindow constructor\n")

        s = QtWebKit.QWebSettings.globalSettings()
        s.setAttribute(QtWebKit.QWebSettings.LocalContentCanAccessRemoteUrls, True);
        s.setAttribute(QtWebKit.QWebSettings.PluginsEnabled, False);
        s.setAttribute(QtWebKit.QWebSettings.DeveloperExtrasEnabled, True);
        s.setAttribute(QtWebKit.QWebSettings.LocalStorageEnabled, True);
        s.setAttribute(QtWebKit.QWebSettings.JavascriptCanOpenWindows, True);
        s.setAttribute(QtWebKit.QWebSettings.JavascriptCanCloseWindows, True);

        self.main_window = QtGui.QMainWindow(rvqt.sessionWindow())
        self.gma_web_view = QtWebKit.QWebView(self.main_window)

        p = getCppPointer(self.gma_web_view.page().mainFrame())
        rvc.javascriptExport(p[0])

        url = QtCore.QUrl(serverURL + "/page/media_center")
        # url = QtCore.QUrl("http://google.com")
        sys.stderr.write("opening URL '%s'\n" % str(url))
        self.gma_web_view.load(url)

        self.main_window.setCentralWidget(self.gma_web_view)
        self.main_window.resize(1200, 800);
        self.main_window.show()

        sys.stderr.write("************************************************** pGMAWindow constructor done\n")

