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
import traceback
from rv import rvtypes
from rv import commands
from pymu import MuSymbol
import rv
from PySide import QtGui


#import bootstrap # need to get at the module itself

sys.path.append("/Users/manne/Documents/work_dev/toolkit/tk-core/python")
from tank_vendor import shotgun_base, shotgun_deploy, shotgun_authentication


# Assuming Toolkit is available in the path.
from tank_vendor.shotgun_api3 import Shotgun
from tank_vendor.shotgun_authentication.user import ShotgunUser
from tank_vendor.shotgun_authentication.user_impl import ShotgunUserImpl

# set up a toolkit logger for the RV package
log = shotgun_base.get_sgtk_logger("rv_bootstrap")


class RVUserImpl(ShotgunUserImpl):
    """
    A user that authenticates to the Shotgun server using a session token.
    """

    def __init__(self, host, login, session_token, http_proxy):
        """
        Constructor.
        :param host: Host for this Shotgun user.
        :param login: Login name for the user.
        :param session_token: Session token for the user. If session token is None
            the session token will be looked for in the users file.
        :param http_proxy: HTTP proxy to use with this host. Defaults to None.
        :raises IncompleteCredentials: If there is not enough values
            provided to initialize the user, this exception will be thrown.
        """
        super(RVUserImpl, self).__init__(host, http_proxy)

        self._login = login
        self._session_token = session_token

    def get_login(self):
        """
        Return the login name for this user.
        :returns: The login name string.
        """
        return self._login

    def create_sg_connection(self):
        """
        Create a Shotgun instance using the script user's credentials.
        :returns: A Shotgun instance.
        """
        return Shotgun(
            self.get_host(),
            session_token=self._session_token,
            http_proxy=self.get_http_proxy()
        )

    def __repr__(self):
        """
        Return a string reprensentation of the user.
        :returns: A string containing login and site.
        """
        return "<RVUser %s @ %s>" % (self._login, self._host)

    def __str__(self):
        """
        Return the name of the user.
        :returns: A string.
        """
        return self._login


class ToolkitBootstrap(rvtypes.MinorMode):


    def __init__(self):

        rvtypes.MinorMode.__init__(self)

        self.init("toolkit_bootstrap", None, None)

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

        # Get default session info from slutils (rv/shotgun licensing) module
        (url, login, token) = self._get_default_rv_auth_session()

        # create an internal private method for auth (can this be done differently?
        internal_user_obj = RVUserImpl(url, login, token, self._http_proxy_from_env_vars())

        # wrap in an official user object
        user = ShotgunUser(internal_user_obj)

        # i am guessing this will authenticate the user if needed?
        # otherwise it's not needed.
        _ = user.create_sg_connection()

        # manne - logging out?? what happens? Need to check.

        # XXX what if previous session is not the server we want ?
        # XXX this forces restart if we fail here.  we instead should
        #     wait for login process to succeed and then continue.


        # now bootstrap
        mgr = shotgun_deploy.ToolkitManager(user)
        mgr.base_config_location = {
            "type": "git",
            "path": "git@github.com:shotgunsoftware/tk-rv.git",
            "version": "latest"
        }
        mgr.bootstrap_engine("tk-rv")


    def _get_default_rv_auth_session(self):
        """
        Returns a tuple with session details from rv authentication

        :returns: tuple (url, login, token) with shotgun url, login and session token
        """
        rv.runtime.eval("require slutils;", [])
        # get session data from RV
        (last_session, sessions) = MuSymbol("slutils.retrieveSessionsData")()
        log.debug("Session data: %s" % last_session)
        # grab the first three tokens out of the string
        (url, login, token) = last_session.split("|")[:3]
        # return (url, login, token)
        return url, login, token

    def _http_proxy_from_env_vars(self):

        # Note from shotgun api source about expected proxy string
        #
        #   :param http_proxy: Optional, URL for the http proxy server, in the
        #   form [username:pass@]proxy.com[:8080]

        user = os.getenv("RV_NETWORK_PROXY_USER", None)
        passwd = os.getenv("RV_NETWORK_PROXY_PASSWORD", None)
        host = os.getenv("RV_NETWORK_PROXY_HOST", None)
        port = os.getenv("RV_NETWORK_PROXY_PORT", None)

        http_proxy = None

        if host:
            http_proxy = host
            if user:
                if passwd:
                    http_proxy = user + ":" + passwd + "@" + http_proxy
                else :
                    http_proxy = user + "@" + http_proxy
            if port:
                http_proxy += ":" + port

        return http_proxy


def createMode():
    "Required to initialize the module. RV will call this function to create your mode."
    return ToolkitBootstrap()
