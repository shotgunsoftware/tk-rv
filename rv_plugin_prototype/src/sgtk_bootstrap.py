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
from rv import rvtypes
import rv
from PySide import QtGui, QtCore

# set up logging
log = logging.getLogger("sgtk_rv_bootstrap")
log.setLevel(logging.DEBUG)

class EscapedHtmlFormatter(logging.Formatter):

    def __init__(self, fmt, datefmt=None):
        logging.Formatter.__init__(self, fmt, datefmt)

    def format(self, record):
        result = logging.Formatter.format(self, record)
        return cgi.escape(result)

log_handler = logging.StreamHandler()
log_handler.setFormatter(EscapedHtmlFormatter("%(asctime)s %(name)s %(levelname)s: %(message)s"))
log.addHandler(log_handler)


class ToolkitBootstrap(rvtypes.MinorMode):
    """
    Creates a tk rv engine
    """

    def __init__(self):
        """
        Constructor.
        """
        rvtypes.MinorMode.__init__(self)
        self.init("sgtk_bootstrap", None, None)

    def activate(self):
        rv.rvtypes.MinorMode.activate(self)

        # leaving this in here for later. Gets a path to the resources folder
        # but not sure exactly what gets put there...
        # payload_path = os.path.join(self.supportPath(bootstrap, "bootstrap"), "payload")


        log.info("------------------------------------------------------------------")
        log.info("Starting up remote configuration!")
        log.info("")
        log.info("For this, we need to have a core to 'seed' the process - a place ")
        log.info("where we can run the actual bootstrap code from.")
        log.info("")
        log.info("This will be picked up from the TK_CORE env var if set.")
        log.info("------------------------------------------------------------------")

        default_core = os.environ.get("TK_CORE") or "/tmp/tk-core"

        (core, status) = QtGui.QInputDialog.getText(
            None,
            "Toolkit Bootstrap",
            "Where is core:",
            QtGui.QLineEdit.Normal,
            default_core)

        if not status:
            return

        # append python path to get to the actual code
        core = os.path.join(core, "python")

        log.info("Looking for core here: %s" % str(core))

        # now we can kick off sgtk
        sys.path.append(core)

        # import bootstrapper
        from tank_vendor import shotgun_base, shotgun_deploy, shotgun_authentication

        # import authentication code
        from sgtk_auth import get_toolkit_user

        # bind toolkit logging to our logger
        sgtk_root_logger = shotgun_base.get_sgtk_logger()
        sgtk_root_logger.setLevel(logging.DEBUG)
        sgtk_root_logger.addHandler(log_handler)

        # now figure out which config to use
        default_uri = "sgtk:git_branch:git@github.com%3Ashotgunsoftware/tk-config-rv.git:master:latest"

        (uri, status) = QtGui.QInputDialog.getText(
            None,
            "Toolkit Bootstrap",
            "Config Uri:",
            QtGui.QLineEdit.Normal,
            default_uri)

        if not status:
            return

        # Get an authenticated user object from rv's security architecture
        user = get_toolkit_user()
        log.info("Will connect using %r" % user)

        # now bootstrap
        log.info("Ready for bootstrap!")
        mgr = shotgun_deploy.ToolkitManager(user)

        # hint bootstrapper about our name space so that we don't pick
        # the site config for maya or desktop
        mgr.set_namespace("rv")

        # if nothing is found in Shotgun, kick off using the base config
        mgr.set_base_configuration(uri)

        # and bootstrap the tk-rv engine into an empty context
        mgr.bootstrap_engine("tk-rv")


    def deactivate(self):
        rv.rvtypes.MinorMode.deactivate(self)
        log.info("Shutting down engine...")
        import sgtk
        sgtk.platform.current_engine().destroy()
        log.info("Engine is down.")

def createMode():
    "Required to initialize the module. RV will call this function to create your mode."
    return ToolkitBootstrap()
