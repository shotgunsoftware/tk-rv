
import os
#import re
import sys
import traceback

from BaseHTTPServer import BaseHTTPRequestHandler,HTTPServer
import ssl
import sys

from rv import rvtypes
from rv import commands
from rv import extra_commands
from rv import qtutils

from PySide import QtGui
from PySide import QtWebKit
from PySide import QtCore

# Assuming Toolkit is available in the path.
from tank_vendor.shotgun_api3 import Shotgun
from tank_vendor.shotgun_authentication.user import ShotgunUser
from tank_vendor.shotgun_authentication.user_impl import ShotgunUserImpl

def deb(s, addNL=True) :
    if (addNL) :
        sys.stderr.write(s + "\n");
    else :
        sys.stderr.write(s);

PORT_NUMBER = 51794

class RvHttpHandler(BaseHTTPRequestHandler) :
    
    def printStuff (self) :
        deb ("Command: %s" % self.command)
        deb ("Path: %s" % self.path)
        for h in self.headers.headers :
            deb (h, False)
        szString = self.headers.getheader('content-length')
        if szString :
            sz = int(szString)
        else :
            sz = 0
        self.content = ""
        lines = self.rfile.read(sz)
        for l in lines :
            self.content += l
            deb (l, False)

    def do_GET (self) :
        deb("*************************************************** GET")
        self.printStuff()
        deb ("GET: sending back 'RV knows where you live !'")
        self.send_response(200)
        self.send_header('Content-type','text/html')
        self.end_headers()
        # Send the html message
        self.wfile.write("RV knows where you live !")
        return

    def do_POST(self):
        deb("*************************************************** POST")
        self.printStuff()
        deb ("POST: sending back 'RESPONSE !'")
        self.send_response(200)
        self.send_header('Content-type','text/html')
        self.send_header("Access-Control-Allow-Origin", self.headers.getheader('Origin'))
        self.end_headers()
        self.wfile.write("RESPONSE !")

        qtutils.sessionWindow().show()
        getattr(qtutils.sessionWindow(), "raise")()
        qtutils.sessionWindow().activateWindow()

        #   Allowing aribitrary events from the web would be (another) giant
        #   security hole (in particular it would allow 'remote-eval' events).
        #   Instead we force an "external-" prefix on all event names from this
        #   source.  Event handlers can then decide what to do with the event.
        #
        eventName = "external-" + self.path.split('/')[-1]
        eventContents = self.content.strip()

        deb("do_POST ---------------------------- current thread " + str(QtCore.QThread.currentThread()))
        deb("calling event handler")
        self.server.sendEvent.emit(eventName, eventContents)
        deb("calling event handler done")

    def do_OPTIONS(self):
        deb("*************************************************** OPTIONS")
        self.printStuff()
        deb ("OPTIONS: allow origin '%s', headers '%s'" % (self.headers.getheader('Origin'), self.headers.getheader("Access-Control-Request-Headers")))
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin",  self.headers.getheader('Origin'))
        self.send_header("Access-Control-Allow-Headers", self.headers.getheader("Access-Control-Request-Headers"))
        self.end_headers()

def createServer(cert, key) :

    httpServer = None
    try :
        httpServer = HTTPServer(('', PORT_NUMBER), RvHttpHandler)
        httpServer.socket = ssl.wrap_socket (
            httpServer.socket, 
            certfile=cert,
            keyfile=key,
            server_side=True)

        deb ('Started httpserver on port %d' % PORT_NUMBER)
    except :
        if (httpServer and httpServer.socket) :
            httpServer.socket.close()
        raise

    return httpServer


class RvServerThread (QtCore.QThread):
    
    sendEvent = QtCore.Signal(str, str)

    #
    #  XXX temp hack for self-signing
    #

    certFile = '/var/tmp/rv-server.pem' 
    keyFile  = '/var/tmp/rv-key.key' 
    signFile = '/var/tmp/rv-server.csr'

    signCmd = """
    rm -f %s %s %s 
    openssl genrsa -out %s 1024
    printf "US\nCA\nSF\nShotgun Software\ntk-rv-shotgunreview\n\n\n\n\n" | openssl req -new -key %s -out %s
    openssl x509 -req -days 366 -in %s -signkey %s -out %s
    """ % (certFile, keyFile, signFile, keyFile, keyFile, signFile, signFile, keyFile, certFile)

    def __init__(self, callback):

        super(RvServerThread, self).__init__(qtutils.sessionWindow())

        self.sendEvent.connect(callback)

        try :
            self.httpServer = createServer(self.certFile, self.keyFile)
        except :
            try :
                deb("HTTP Server creation failed, trying to self-sign ...")
                os.system(self.signCmd)
                self.httpServer = createServer(self.certFile, self.keyFile)
            except Exception, e:
                traceback.format_exc()
                sys.stderr.write("WARNING: Could not create RV https server\n")
                self.httpServer = None
                raise

    def run(self):

        self.httpServer.sendEvent = self.sendEvent
        self.httpServer.serve_forever()

        self.exec_()

