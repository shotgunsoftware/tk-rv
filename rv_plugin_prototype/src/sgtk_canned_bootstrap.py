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
import sys
import cgi
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

# this is a baked config. We use a specific set of app versions.
BOOTSTRAP_BASE = {
    "type": "git_branch",
    "path": "git@github.com:shotgunsoftware/tk-config-rv.git",
    "branch": "baked",
    "version": "8d3ebd2"
}


class ToolkitCannedBootstrap(rvtypes.MinorMode):
    """
    Creates a tk rv engine
    """

    def __init__(self):
        """
        Constructor.
        """
        rvtypes.MinorMode.__init__(self)
        self.init("sgtk_canned_bootstrap", None, None)

    def activate(self):
        rv.rvtypes.MinorMode.activate(self)

        log.info("------------------------------------------------------------------")
        log.info("Starting up baked configuration!")
        log.info("")
        log.info("This will be picked up from the TK_CACHE env var if set.")
        log.info("------------------------------------------------------------------")

        default_bundle_cache = os.environ.get("TK_CACHE") or "/tmp/tk-cache"

        (bundle_cache, status) = QtGui.QInputDialog.getText(
            None,
            "Toolkit Bootstrap",
            "Bundle cache dir:",
            QtGui.QLineEdit.Normal,
            default_bundle_cache
        )

        if not status:
            return

        # ok at this point we know where our core is located, it's inside the
        # bundle cache! So go ahead and import it.
        #
        # note: when the core is in the app store, this url will be simpler.
        #       could also so something that scans for latest app store cache
        #       inside the bundle cache if that makes more sense.
        core_path = os.path.join(
            bundle_cache,
            "git",
            "tk-core.git",
            "8722b46",
            "python"
        )

        log.info("Looking for core here: %s" % str(core_path))

        # now we can kick off sgtk
        sys.path.append(core_path)

        log.info("------------------------------------------------------------------")
        log.info("Importing python modules...")

        # import bootstrapper
        from tank_vendor import shotgun_base, shotgun_deploy, shotgun_authentication

        # import authentication code
        from sgtk_auth import get_toolkit_user

        log.info("Setting up logging...")

        # bind toolkit logging to our logger
        sgtk_root_logger = shotgun_base.get_sgtk_logger()
        sgtk_root_logger.setLevel(logging.DEBUG)
        sgtk_root_logger.addHandler(log_handler)

        # Get an authenticated user object from rv's security architecture
        log.info("Setting up authenticated user...")
        user = get_toolkit_user()
        log.info("Will connect using %r" % user)

        # now bootstrap
        log.info("Creating bootstrapper...")
        mgr = shotgun_deploy.ToolkitManager(user)

        # hint bootstrapper about our name space so that we don't pick
        # the site config for maya or desktop
        mgr.set_namespace("rv")

        # tell it where to go look for apps
        mgr.set_bundle_cache_root(bundle_cache)

        # if nothing is found in Shotgun, kick off using the base config
        mgr.set_base_configuration(BOOTSTRAP_BASE)

        # and bootstrap the tk-rv engine into an empty context
        log.info("Executing bootstrap...")
        mgr.bootstrap_engine("tk-rv")

        log.info("...bootstrap complete!")



    def deactivate(self):
        rv.rvtypes.MinorMode.deactivate(self)
        log.info("Shutting down engine...")
        import sgtk
        sgtk.platform.current_engine().destroy()
        log.info("Engine is down.")



def createMode():
    "Required to initialize the module. RV will call this function to create your mode."
    return ToolkitCannedBootstrap()
