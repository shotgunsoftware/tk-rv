import os
import re
import sys
import traceback

from rv import rvtypes
from rv import commands

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
    A user that authenticates to the server using a session token.
    """

    def __init__(self, host, login, session_token, http_proxy):
        """
        Constructor.

        :param host: Host for this Flow Production Tracking user.
        :param login: Login name for the user.
        :param session_token: Session token for the user. If session token is None
            the session token will be looked for in the users file.
        :param http_proxy: HTTP proxy to use with this host. Defaults to None.

        :raises IncompleteCredentials: If there is not enough values
            provided to initialize the user, this exception will be thrown.
        """
        super().__init__(host, http_proxy)

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
            http_proxy=self.get_http_proxy(),
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
        super().__init__()

        # INITIALIZE mode
        self.init(TK_RV_MODE_NAME, [], None, [])

        # START rv engine after initializing mode because the engine needs
        # mode name to create PTR menu.
        self.__engine = self.start_engine()

    @property
    def engine(self):
        if not self.__engine:
            self.__engine = self.start_engine()
        return self.__engine

    @staticmethod
    def http_proxy_from_env_vars():
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
                else:
                    http_proxy = user + "@" + http_proxy
            if port:
                http_proxy += ":" + port

        return http_proxy

    def start_engine(self):
        engine = None

        try:
            import tank
        except Exception as e:
            print("ERROR: Failed to import tank.\n", file=sys.stderr)
            return engine

        # Defaults to tk-rv if no other engine name found in environment.
        engine_name = os.environ.get("TANK_ENGINE", "tk-rv")

        if os.environ.get("TANK_CONTEXT"):
            try:
                context = tank.context.deserialize(os.environ.get("TANK_CONTEXT"))
            except Exception as e:
                err = traceback.format_exc()
                print(
                    "WARNING: Could not create context! Tank will be disabled: {0}".format(
                        traceback.format_exc()
                    ),
                    file=sys.stderr,
                )
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

                user = ShotgunUser(
                    RVUserImpl(
                        url, login, token, ShotgunToolkit.http_proxy_from_env_vars()
                    )
                )
                sg_conn = user.create_sg_connection()
                sgtk.set_authenticated_user(user)

                # XXX what if previous session is not the server we want ?
                # XXX this forces restart if we fail here.  we instead should
                #     wait for login process to succeed and then continue.

            except:
                err = traceback.print_exc()
                commands.alertPanel(
                    True,
                    commands.ErrorAlert,
                    "Login Session Invalid",
                    "Login with RV Flow Production Tracking session token failed; "
                    "please use the File Menu's "
                    '"License Manager" to log in to '
                    "the server and re-start RV.",
                    "Continue",
                    None,
                    None,
                )
                return None

            projectName = "Big Buck Bunny"
            if os.environ.get("TANK_PROJECT_NAME"):
                projectName = os.environ.get("TANK_PROJECT_NAME")

            print("DEBUG: find project '%s'.\n" % projectName, file=sys.stderr)
            project = sg_conn.find("Project", [["name", "is", projectName]])
            print("DEBUG:     find result '%s'.\n" % str(project), file=sys.stderr)

            tk = sgtk.sgtk_from_entity(project[0]["type"], project[0]["id"])

            context = tk.context_from_entity_dictionary(project[0])

        try:
            print("INFO: Starting TK-RV Engine", sys.stderr)
            engine = tank.platform.start_engine(engine_name, context.tank, context)
        except Exception as e:
            print(
                "WARNING: Could not start engine: "
                "{0}".format(traceback.format_exc()),
                file=sys.stderr,
            )
            return engine

        # clean up temp env vars
        for var in ["TANK_ENGINE", "TANK_CONTEXT", "TANK_FILE_TO_OPEN"]:
            if var in os.environ:
                del os.environ[var]

        return engine


def createMode():
    return ShotgunToolkit()
