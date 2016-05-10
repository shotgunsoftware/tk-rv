# Copyright (c) 2016 Shotgun Software Inc.
#
# CONFIDENTIAL AND PROPRIETARY
#
# This work is provided "AS IS" and subject to the Shotgun Pipeline Toolkit
# Source Code License included in this distribution package. See LICENSE.
# By accessing, using, copying or modifying this work you indicate your
# agreement to the Shotgun Pipeline Toolkit Source Code License. All rights
# not expressly granted therein are reserved by Shotgun Software Inc.

import logging
import cgi
import sys
import os
import platform
import json

from PySide import QtCore, QtGui

from pymu import MuSymbol

import rv
import rv.rvtypes as rvt
import rv.commands as rvc
import rv.extra_commands as rve
import rv.qtutils as rvqt

def sgtk_dist_dir():
    executable_dir = os.path.dirname(os.environ["RV_APP_RV"])

    if (platform.system == "Darwin"):
        content_dir = os.path.split(os.path.split(executable_dir)[0])[0]
    else:
        content_dir = os.path.split(executable_dir)[0]
    
    return os.path.join(content_dir, "src", "python", "sgtk")

class ToolkitBootstrap(rvt.MinorMode):
    """
    An RV mode that will handle bootstrapping SGTK and starting
    up the tk-rv engine. The mode expects an installation of
    tk-core to be present in the same directory underneath an
    "sgtk_core" subdirectory. Alternatively, an environment variable
    "TK_CORE" can be set to an alternate installation of tk-core
    to override the default behavior.
    """
    def __init__(self):
        """
        Initializes the RV mode. An environment variable "TK_RV_MODE_NAME"
        will be set to the name of this mode. That variable can then be
        used by other logic to generate menu items in RV associated with
        this mode.
        """
        super(ToolkitBootstrap, self).__init__()

        self._mode_name = "sgtk_bootstrap"
        self.init(self._mode_name, None,
                [
                    ("external-gma-play-entity", self.external_gma_play_entity, ""),
                    ("external-gma-compare-entities", self.external_gma_compare_entities, ""),
                    ("external-sgtk-launch-app", self.launch_app, "")
                ],
                [("SG Review", [
                    # ("HTTP Server", None, None, lambda: rvc.DisabledMenuState),
                    # ("    Start Server", self.http_server_setup, None, lambda: rvc.UncheckedMenuState),
                    # ("    Test Certificate", self.test_certificate, None, lambda: rvc.UncheckedMenuState),
                    # ("_", None),
                    # ("GMA WebView", self.gma_web_view, None, lambda: rvc.UncheckedMenuState),
                    # ("_", None),
                    # ("Test Cuts", None, None, lambda: rvc.DisabledMenuState),
                    # ("    08_a-team_client_cut_002",                               
                    #     self.play_entity_factory("Cut", 6), None, lambda: rvc.UncheckedMenuState),
                    # ("    08_a-team_base_layer_example_versions_that_fit_cut_001", 
                    #     self.play_entity_factory("Cut", 1), None, lambda: rvc.UncheckedMenuState),
                    # ("    Select a Cut by ID ...", 
                    #     self.play_entity_dialog_factory("Cut"), None, lambda: rvc.UncheckedMenuState),
                    # ("Test Versions", None, None, lambda: rvc.DisabledMenuState),
                    # ("    BBB_08_a-team_010_ANIM_001", 
                    #     self.play_entity_factory("Version", 6048), None, lambda: rvc.UncheckedMenuState),
                    # ("    BBB_08_a-team_001_ANIM_001", 
                    #     self.play_entity_factory("Version", 6004), None, lambda: rvc.UncheckedMenuState),
                    # ("    BBB_09_tree_trunk_011_ANIM_001", 
                    #     self.play_entity_factory("Version", 6023), None, lambda: rvc.UncheckedMenuState),
                    # ("    Select a Version by ID ...", 
                    #     self.play_entity_dialog_factory("Version"), None, lambda: rvc.UncheckedMenuState),
                    # ("Test Playlists", None, None, lambda: rvc.DisabledMenuState),
                    # ("    Alan's Playlist 2/19/2016", 
                    #     self.play_entity_factory("Playlist", 62), None, lambda: rvc.UncheckedMenuState),
                    # ("    Select a Playlist by ID ...", 
                    #     self.play_entity_dialog_factory("Playlist"), None, lambda: rvc.UncheckedMenuState),
                    # ("_", None)]
                    ]
                )])

        self.http_server_thread = None
        self.webview = None
        self.server_url = None

        # The menu generation code makes use of the TK_RV_MODE_NAME environment
        # variable. Each menu item that is created in RV is associated with a
        # mode identified by its name. We need to make a note of our name so we
        # can add menu items for this mode later.

        os.environ["TK_RV_MODE_NAME"] = self._mode_name

    def play_entity_factory (self, entity, id):

        def play_entity(event):
            contents = '{"type":"' + entity + '","id":' + str(id) + '}'
            rvc.stop()
            rvc.sendInternalEvent("id_from_gma", contents)
            rvc.play()

        return play_entity

    def play_entity_dialog_factory (self, entity):

        def dialog(event):
            """
            Opens the text version of the input dialog
            """
            idStr, result = QtGui.QInputDialog.getText(rvqt.sessionWindow(), "I'm a text Input Dialog!",
                                        "What is your favorite " + entity + " ?")
            if result:
                try:
                    contents = '{"type":"' + entity + '","id":' + str(int(idStr)) + '}'
                    rvc.stop()
                    rvc.sendInternalEvent("id_from_gma", contents)
                    rvc.play()
                except:
                    log.error("could not convert '%s' to %s ID" % (idStr, entity))

        return dialog

    def gma_web_view (self, event) :

        import sgtk_webview_gma

        self.webview = sgtk_webview_gma.pyGMAWindow(self.server_url)

    def external_gma_compare_entities(self, event):
        rvc.sendInternalEvent("compare_ids_from_gma", event.contents())
        rvc.redraw()

    def external_gma_play_entity(self, event):
        self.http_event_callback(event.name(), event.contents())
        rvc.redraw()

    def http_event_callback(self, name, contents):
        log.debug("callback ---------------------------- current thread " + str(QtCore.QThread.currentThread()))
        rve.displayFeedback(name + " " + contents, 2.5)
        if (name == "external-gma-play-entity") :
            internalName = "id_from_gma"

            # Currently lower-level code only supports singular "id", but GMA
            # will send (sometimes) multiple ids.  For now pull out the first
            # one and send it on.
            #
            gma_data = json.loads(contents)
            if gma_data.has_key("ids") and not gma_data.has_key("id"):
                gma_data["id"] = gma_data["ids"][0]
            contents = json.dumps(gma_data)

            log.debug("callback sendEvent %s '%s'" % (internalName, contents))
            rvc.sendInternalEvent(internalName, contents)
        
    def http_server_setup(self, event):
        import sgtk_rvserver
        self.http_server_thread = sgtk_rvserver.RvServerThread(self.http_event_callback)
        self.http_server_thread.start()

    def test_certificate(self, event):

        # Start up server if it's not already going
        if (not self.http_server_thread) :
            self.http_server_setup(None)

        # Get port number from server itself
        url = "https://localhost:" + str(self.http_server_thread.httpServer.server_address[1])
        log.debug("open url: '%s'" % url)
        rvc.openUrl(url)

    def launch_app(self, event):
        app_data = json.loads(event.contents())

        if (app_data["app"] == "tk-multi-importcut"):
            import sgtk
            eng = sgtk.platform.current_engine()
            if (eng):
                # XXX Need to check URL in data, and pass on project ID if there is one
                callback = eng.commands.get("Cut Import", dict()).get("callback")
                if (callback):
                    callback()
        else:
            log.error("don't know how to launch app '%s'" % app_data["app"])

    def activate(self):
        """
        Activates the RV mode and bootstraps SGTK.
        """
        rvt.MinorMode.activate(self)

        bundle_cache_dir = os.path.join(sgtk_dist_dir(), "bundle_cache")

        core = os.path.join(bundle_cache_dir, "manual", "tk-core", "v1.0.11")
        core = os.environ.get("RV_TK_CORE") or core

        # append python path to get to the actual code
        core = os.path.join(core, "python")

        log.info("Looking for tk-core here: %s" % str(core))

        # now we can kick off sgtk
        sys.path.append(core)

        # import bootstrapper
        from tank_vendor import shotgun_base, shotgun_deploy, shotgun_authentication

        # import authentication code
        from sgtk_auth import get_toolkit_user

        # allow dev to override log level
        log_level = logging.WARNING
        if (os.environ.has_key("RV_TK_LOG_DEBUG")) :
            log_level = logging.DEBUG

        # bind toolkit logging to our logger
        sgtk_root_logger = shotgun_base.get_sgtk_logger()
        sgtk_root_logger.setLevel(log_level)
        sgtk_root_logger.addHandler(log_handler)

        # Get an authenticated user object from rv's security architecture
        (user, url) = get_toolkit_user()
        self.server_url = url
        log.info("Will connect using %r" % user)

        # Now do the bootstrap!
        log.info("Ready for bootstrap!")
        mgr = shotgun_deploy.ToolkitManager(user)

        # Hint bootstrapper about our namespace so that we don't pick
        # the site config for Maya or Desktop.
        mgr.namespace = "rv"

        # In disted code, by default, all TK code is read from the
        # 'bundle_cache' baked during the build process.
        mgr.bundle_cache_fallback_paths = [ bundle_cache_dir ]

        dev_config = os.environ.get("RV_TK_DEV_CONFIG")

        if (dev_config):
            # Use designated developer's tk-config-rv instead of disted one.
            mgr.base_configuration = dict(
                type="dev",
                path=dev_config,
            )
        else:
            mgr.base_configuration = dict(
                type="manual",
                name="tk-config-rv",
                version="v1.0.11",
            )

        # Bootstrap the tk-rv engine into an empty context!
        mgr.bootstrap_engine("tk-rv")
        log.info("Bootstrapping process complete!")


    def deactivate(self):
        """
        Deactivates the mode and tears down the currently-running
        SGTK engine.
        """
        import sgtk
        rvt.MinorMode.deactivate(self)

        log.info("Shutting down engine...")

        if sgtk.platform.current_engine():
            sgtk.platform.current_engine().destroy()

        log.info("Engine is down.")


###############################################################################
# functions

def createMode():
    """
    Required to initialize the module. RV will call this function
    to create your mode.
    """
    return ToolkitBootstrap()


###############################################################################
# logging

log = logging.getLogger("sgtk_rv_bootstrap")
log.setLevel(logging.INFO)

# note: the RV console treats log information as html. As a consequence, all
# <html like tokens> will simply disappear when shown in the RV console. These
# <tokens> are common in toolkit, often returned by __repr__() as object identifiers.
# 
# To ensure we can see everything in the RV console, html escape all log messages
# before they hit the console.
#
class EscapedHtmlFormatter(logging.Formatter):
    def __init__(self, fmt, datefmt=None):
        logging.Formatter.__init__(self, fmt, datefmt)

    def format(self, record):
        result = logging.Formatter.format(self, record)
        return cgi.escape(result)

log_handler = logging.StreamHandler()
log_handler.setFormatter(
    EscapedHtmlFormatter("%(asctime)s %(name)s %(levelname)s: %(message)s")
)
log.addHandler(log_handler)
