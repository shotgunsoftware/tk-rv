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
import os
from rv import rvtypes
from rv import commands
from pymu import MuSymbol
import rv
from PySide import QtGui

# @todo - how do I make a python *module* inside of RV land so
#         i can use relative imports?
from sgtk_auth import get_toolkit_user

#import bootstrap # need to get at the module itself

sys.path.append("/Users/manne/Documents/work_dev/toolkit/tk-core/python")
from tank_vendor import shotgun_base, shotgun_deploy, shotgun_authentication


# Assuming Toolkit is available in the path.
from tank_vendor.shotgun_api3 import Shotgun
from tank_vendor.shotgun_authentication.user import ShotgunUser
from tank_vendor.shotgun_authentication.user_impl import ShotgunUserImpl

# set up a toolkit logger for the RV package
log = shotgun_base.get_sgtk_logger("sgtk_bootstrap")


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

        # leaving this in here for later. Gets a path to the resources folder
        # but not sure exactly what gets put there...
        # payload_path = os.path.join(self.supportPath(bootstrap, "bootstrap"), "payload")

        # set up logging
        root_logger = shotgun_base.get_sgtk_logger()
        root_logger.setLevel(logging.DEBUG)
        ch = logging.StreamHandler()
        formatter = logging.Formatter("%(levelname)s %(message)s")
        ch.setFormatter(formatter)
        root_logger.addHandler(ch)

        log.warning("hello bootstrap!")

        # Get an authenticated user object from rv's security architecture
        user = get_toolkit_user()
        log.info("Will connect using %r" % user)

        # now bootstrap
        mgr = shotgun_deploy.ToolkitManager(user)
        mgr.set_base_configuration({
            "type": "git",
            "path": "git@github.com:shotgunsoftware/tk-config-rv.git",
            "branch": "master"
        })
        mgr.bootstrap_engine("tk-rv")




def createMode():
    "Required to initialize the module. RV will call this function to create your mode."
    return ToolkitBootstrap()
