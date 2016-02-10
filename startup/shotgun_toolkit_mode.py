
import os
import re
import sys
import traceback

from rv import rvtypes
from rv import commands
from PySide import QtGui

# Define the integration mode name we'll be useing.
TK_RV_MODE_NAME = "tk_rv_mode"

# Put the integration mode name in the environment so the engine can pick it
# up.
# NOTE TO SELF: is this how we like it?
os.environ["TK_RV_MODE_NAME"] = TK_RV_MODE_NAME

# Assuming Toolkit is available in the path.
from tank_vendor.shotgun_api3 import Shotgun
from tank_vendor.shotgun_authentication.user import ShotgunUser
from tank_vendor.shotgun_authentication.user_impl import ShotgunUserImpl
import sgtk

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
            self.get_host(), session_token=self._session_token,
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

class ShotgunToolkit(rvtypes.MinorMode):

    def __init__(self):

        super(ShotgunToolkit, self).__init__()

        # INITIALIZE mode
        self.init(TK_RV_MODE_NAME, [], None, [])

        # START rv engine after initializing mode because the engine needs
        # mode name to create SGTK menu.
        self.__engine = self.start_engine()

    @property
    def engine(self):
        if not self.__engine:
            self.__engine = self.start_engine()
        return self.__engine

    def start_engine(self):
        engine = None

        try:
            import tank
        except Exception, e:
            sys.stderr.write("ERROR: Failed to import tank.\n")
            return engine

        # Defaults to tk-rv if no other engine name found in environment.
        engine_name = os.environ.get("TANK_ENGINE", "tk-rv")

        if os.environ.get("TANK_CONTEXT"):

            try:
                context = tank.context.deserialize(os.environ.get("TANK_CONTEXT"))
            except Exception, e:
                err = traceback.format_exc()
                sys.stderr.write("WARNING: Could not create context! "
                      "Tank will be disabled: {0}".format(traceback.format_exc()))
                return engine
        else:
            import sgtk

            # if you want to force a Toolkit-style login, here's how:
            #
            # import tank_vendor.shotgun_authentication
            # sa = tank_vendor.shotgun_authentication.ShotgunAuthenticator()
            # sa.get_user_from_prompt()
            # user = sa.get_user()

            try:
                import slutils_py

                # Get default session info from slutils (rv/shotgun licensing) module
                (url, login, token) = slutils_py.defaultSession()

                # XXX Need format of http_proxy arg to replace None below
                user = ShotgunUser(RVUserImpl(url, login, token, None))
                sg_conn = user.create_sg_connection()
                sgtk.set_authenticated_user(user)

                # XXX what if previous session is not the server we want ?
                # XXX this forces restart if we fail here.  we instead should
                #     wait for login process to succeed and then continue.

            except:
                commands.alertPanel (True, commands.ErrorAlert, "Login Session Invalid", 
                        "Login with RV Shotgun session token failed; please use the File Menu's "
                        "\"License Manager\" to log in to the Shotgun server and re-start RV.", 
                        "Continue", None, None);
                return None

            projectName = 'Big Buck Bunny'
            if os.environ.get('TANK_PROJECT_NAME'):
                projectName = os.environ.get('TANK_PROJECT_NAME')

            sys.stderr.write("DEBUG: find project '%s'.\n" % projectName)
            project = sg_conn.find("Project", [["name", "is", projectName]])
            sys.stderr.write("DEBUG:     find result '%s'.\n" % str(project))

            tk = sgtk.sgtk_from_entity(project[0]["type"], project[0]["id"])

            context = tk.context_from_entity_dictionary(project[0])

        try:
            sys.stderr.write("INFO: Starting TK-RV Engine") 
            engine = tank.platform.start_engine(engine_name, context.tank, context)
        except Exception, e:
            sys.stderr.write("WARNING: Could not start engine: "
                  "{0}".format(traceback.format_exc()))
            return engine

        # clean up temp env vars
        for var in ["TANK_ENGINE", "TANK_CONTEXT", "TANK_FILE_TO_OPEN"]:
            if var in os.environ:
                del os.environ[var]

        return engine

def createMode():
    return ShotgunToolkit()
