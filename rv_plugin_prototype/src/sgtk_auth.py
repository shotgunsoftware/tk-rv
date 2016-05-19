# Copyright (c) 2016 Shotgun Software Inc.
#
# CONFIDENTIAL AND PROPRIETARY
#
# This work is provided "AS IS" and subject to the Shotgun Pipeline Toolkit
# Source Code License included in this distribution package. See LICENSE.
# By accessing, using, copying or modifying this work you indicate your
# agreement to the Shotgun Pipeline Toolkit Source Code License. All rights
# not expressly granted therein are reserved by Shotgun Software Inc.

import os
from pymu import MuSymbol
import rv

# at this point, it is assumed that core has been added to the pythonpath
from tank_vendor.shotgun_api3 import Shotgun
from sgtk.authentication import ShotgunUser

# @TODO: This imports a private part of the sgtk.authentication API
from sgtk.authentication.user_impl import ShotgunUserImpl


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
        # The host comes in as unicode. We need to get back to a utf-8 string
        # instead, because unicode strings end up infecting other strings
        # when they're concatinated together.
        if host:
            host = host.encode("utf-8")
        if login:
            login = login.encode("utf-8")
        if session_token:
            session_token = session_token.encode("utf-8")
        if http_proxy:
            http_proxy = http_proxy.encode("utf-8")

        super(RVUserImpl, self).__init__(host, http_proxy)

        self._login = login
        self._session_token = session_token
        self._http_proxy = http_proxy


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
        # Delay the connection so that we can adjust the Config manually.
        shotgun_obj = Shotgun(
            self.get_host(),
            session_token=self._session_token,
            connect=False,
            http_proxy=self._http_proxy
        )
        # The API must be notified that the session token in this case is the
        # result of an RV licensing request.
        shotgun_obj.config.extra_auth_params = { "product": "rv" }
        shotgun_obj.server_caps

        return shotgun_obj

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


def get_toolkit_user():
    """
    Returns a user object representing an authenticated shotgun
    user, ready to be plugged into the shotgun auth framework.

    @todo - does this trigger a login prompt?
    @todo - what if session expires?
    @todo - how does a user log out?
    @todo - how does a user switch site?
    @todo - after someone logs out, how do we trigger a re-boot of toolkit? signals set from RV?

    @return: User Object
    """
    # Get default session info from slutils (rv/shotgun licensing) module
    (url, login, token) = _get_default_rv_auth_session()

    # get proxy server from env vars
    proxy = _http_proxy_from_env_vars()

    # create an internal private method for auth (can this be done differently?
    internal_user_obj = RVUserImpl(url, login, token, proxy)

    # wrap in an official user object
    user = ShotgunUser(internal_user_obj)

    return (user, url)

def _get_default_rv_auth_session():
    """
    Returns a tuple with session details from rv authentication

    :returns: tuple (url, login, token) with shotgun url, login and session token
    """
    rv.runtime.eval("require slutils;", [])
    # get session data from RV
    (last_session, sessions) = MuSymbol("slutils.retrieveSessionsData")()
    # grab the first three tokens out of the string
    (url, login, token) = last_session.split("|")[:3]
    # return (url, login, token)
    return url, login, token

def _http_proxy_from_env_vars():
    """
    Returns a proxy string suitable for use with the Shotgun API.

    :returns: Proxy string on the form [username:pass@]proxy.com[:8080]
    """
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



