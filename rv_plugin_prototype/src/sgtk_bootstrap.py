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
import traceback

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
                None
                )

        self.http_server_thread = None
        self.webview = None
        self.server_url = None
        self.toolkit_initialized = False
        self.licensingStyle = ""

        # The menu generation code makes use of the TK_RV_MODE_NAME environment
        # variable. Each menu item that is created in RV is associated with a
        # mode identified by its name. We need to make a note of our name so we
        # can add menu items for this mode later.

        os.environ["TK_RV_MODE_NAME"] = self._mode_name

     
    #  This is dead code, but keep around in case we want to do this for
    #  debugging.
    #
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

    def server_check (self, contents) :
        gma_data = json.loads(contents)
        if gma_data.has_key("server"):
            sys.stderr.write("-------------------------------- event server '%s' vs '%s'\n" % (gma_data["server"], self.server_url))
            # check 
            if gma_data["server"] == self.server_url:
                return True
            else:
                sys.stderr.write("ERROR: Server mismatch ('%s' vs '%s') Please authenticate RV with your Shotgun server and restart.\n" %
                    (gma_data["server"], self.server_url))
                return False

        return True

    def external_gma_compare_entities(self, event):
        if self.server_check(event.contents()):
            rvc.sendInternalEvent("compare_ids_from_gma", event.contents())
            rvc.redraw()

    def external_gma_play_entity(self, event):
        if self.server_check(event.contents()):
            internalName = "id_from_gma"

            gma_data = json.loads(contents)

            # Currently some lower-level code only supports singular "id", but
            # GMA will send (sometimes) multiple ids.  For now pull out the
            # first one and send it on.
            #
            if gma_data.has_key("ids") and not gma_data.has_key("id"):
                gma_data["id"] = gma_data["ids"][0]

            contents = json.dumps(gma_data)

            log.debug("callback sendEvent %s '%s'" % (internalName, contents))
            rvc.sendInternalEvent(internalName, contents)
            rvc.redraw()

    def launch_app(self, event):
        if not self.server_check(event.contents()):
            return

        app_data = json.loads(event.contents())

        if (app_data["app"] == "tk-multi-importcut"):
            import sgtk
            eng = sgtk.platform.current_engine()
            if (eng):
                # XXX Need to check URL in data, and pass on project ID if there is one
                callback = eng.commands.get("Import Cut", dict()).get("callback")
                if (callback):
                    callback()
        else:
            log.error("don't know how to launch app '%s'" % app_data["app"])

    def initialize(self):
        try:
            bundle_cache_dir = os.path.join(sgtk_dist_dir(), "bundle_cache")

            core = os.path.join(bundle_cache_dir, "manual", "tk-core", "v1.0.20")
            core = os.environ.get("RV_TK_CORE") or core

            # append python path to get to the actual code
            core = os.path.join(core, "python")

            log.info("Looking for tk-core here: %s" % str(core))

            # now we can kick off sgtk
            sys.path.append(core)

            # import bootstrapper
            import sgtk

            # begin logging the toolkit log tree file
            sgtk.LogManager().initialize_base_file_handler("tk-rv")

            # import authentication code
            from sgtk_auth import get_toolkit_user

            # allow dev to override log level
            log_level = logging.WARNING
            if (os.environ.has_key("RV_TK_LOG_DEBUG")) :
                log_level = logging.DEBUG

            # bind toolkit logging to our logger
            sgtk.LogManager().initialize_custom_handler(log_handler)
            # and set the level
            log_handler.setLevel(log_level)

            # Get an authenticated user object from rv's security architecture
            (user, url) = get_toolkit_user()
            self.server_url = url
            log.info("Will connect using %r" % user)

            # Now do the bootstrap!
            log.debug("Ready for bootstrap!")
            mgr = sgtk.bootstrap.ToolkitManager(user)

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
                    version="v1.0.20",
                )

            # Bootstrap the tk-rv engine into an empty context!
            mgr.bootstrap_engine("tk-rv")
            log.debug("Bootstrapping process complete!")

            self.toolkit_initialized = True

        except Exception, e:
            sys.stderr.write(
            "ERROR: Toolkit initialization failed.  Please authenticate RV with your Shotgun server and restart.\n" +
            "**********************************\n")
            traceback.print_exc(None, sys.stderr)
            sys.stderr.write(
            "**********************************\n")
            # raise

    def activate(self):
        """
        Activates the RV mode and bootstraps SGTK.
        """
        rvt.MinorMode.activate(self)

        self.licensingStyle = rvc.readSettings("Licensing", "activeLicensingStyle", "")

        sys.stderr.write("LICENSING STYLE '%s'\n" % self.licensingStyle)

        if self.licensingStyle != "shotgun":
            sys.stderr.write("ERROR: Please authenticate RV with your Shotgun server.\n")
        else:
            self.initialize()

    def deactivate(self):
        """
        Deactivates the mode and tears down the currently-running
        SGTK engine.
        """
        rvt.MinorMode.deactivate(self)

        if self.toolkit_initialized:
            import sgtk

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
