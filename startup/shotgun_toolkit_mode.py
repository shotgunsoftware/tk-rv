import os
import re
import sys
import traceback

from rv import rvtypes

# Define the integration mode name we'll be useing.
TK_RV_MODE_NAME = "tk_rv_mode"

# Put the integration mode name in the environment so the engine can pick it
# up.
# NOTE TO SELF: is this how we like it?
os.environ["TK_RV_MODE_NAME"] = TK_RV_MODE_NAME

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
        print("INFO: PYTHONPATH is %s" % os.environ.get("PYTHONPATH"))
        try:
            import tank
        except Exception, e:
            print("ERROR: Failed to import tank.")
            return engine

        # Defaults to tk-rv if no other engine name found in environment.
        engine_name = os.environ.get("TANK_ENGINE", "tk-rv")

        if os.environ.get("TANK_CONTEXT"):

            try:
                context = tank.context.deserialize(os.environ.get("TANK_CONTEXT"))
            except Exception, e:
                err = traceback.format_exc()
                print("WARNING: Could not create context! "
                      "Tank will be disabled: {0}".format(traceback.format_exc()))
                return engine
        else:
            import sgtk
            import tank_vendor.shotgun_authentication

            sa = tank_vendor.shotgun_authentication.ShotgunAuthenticator()
            # sa.get_user_from_prompt()
            user = sa.get_user()
            sgtk.set_authenticated_user(user)
            sg_conn = user.create_sg_connection()
            
            project = sg_conn.find("Project", [["name", "is", "Big Buck Bunny"]])
            tk = sgtk.sgtk_from_entity(project[0]["type"], project[0]["id"])

            context = tk.context_from_entity_dictionary(project[0])

        try:
            engine = tank.platform.start_engine(engine_name, context.tank, context)
        except Exception, e:
            print("WARNING: Could not start engine: "
                  "{0}".format(traceback.format_exc()))
            return engine

        # clean up temp env vars
        for var in ["TANK_ENGINE", "TANK_CONTEXT", "TANK_FILE_TO_OPEN"]:
            if var in os.environ:
                del os.environ[var]

        return engine

def createMode():
    return ShotgunToolkit()
