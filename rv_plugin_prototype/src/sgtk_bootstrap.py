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

import rv

class ToolkitBootstrap(rv.rvtypes.MinorMode):
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
        self.init(self._mode_name, None, None)

        # The menu generation code makes use of the TK_RV_MODE_NAME
        # environment variable. Each menu that is created in RV is
        # associated with a mode identified by its name. We need to
        # make a note of our name as a result.
        os.environ["TK_RV_MODE_NAME"] = self._mode_name

    def activate(self):
        """
        Activates the RV mode and bootstraps SGTK.
        """
        rv.rvtypes.MinorMode.activate(self)

        core = os.path.join(os.path.dirname(__file__), "sgtk_core")
        core = os.environ.get("TK_CORE") or core

        # append python path to get to the actual code
        core = os.path.join(core, "python")

        log.info("Looking for tk-core here: %s" % str(core))

        # now we can kick off sgtk
        sys.path.append(core)

        # import bootstrapper
        from tank_vendor import shotgun_base, shotgun_deploy, shotgun_authentication

        # import authentication code
        from sgtk_auth import get_toolkit_user

        # bind toolkit logging to our logger
        sgtk_root_logger = shotgun_base.get_sgtk_logger()
        sgtk_root_logger.setLevel(logging.WARNING)
        sgtk_root_logger.addHandler(log_handler)

        # Get an authenticated user object from rv's security architecture
        user = get_toolkit_user()
        log.info("Will connect using %r" % user)

        # Now do the bootstrap!
        log.info("Ready for bootstrap!")
        mgr = shotgun_deploy.ToolkitManager(user)

        # Hint bootstrapper about our namespace so that we don't pick
        # the site config for Maya or Desktop.
        mgr.namespace = "rv"

        mgr.base_configuration = dict(
            # type="dev",
            # path=r"d:\repositories\tk-config-rv",
            path="git@github.com:shotgunsoftware/tk-config-rv.git",
            type="git_branch",
            branch="master",
            version="latest",
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
        rv.rvtypes.MinorMode.deactivate(self)

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
