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
import urlparse

from PySide2 import QtCore, QtGui

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
        self.startup_time = rvc.theTime()

        super(ToolkitBootstrap, self).__init__()

        self._mode_name = "sgtk_bootstrap"
        self.init(self._mode_name, None,
                  [
                      ("external-gma-play-entity", self.pre_process_event, ""),
                      ("external-gma-compare-entities", self.pre_process_event, ""),
                      ("external-sgtk-launch-app", self.pre_process_event, ""),
                      ("external-sgtk-initialize", self.pre_process_event, ""),
                      ("license-state-transition", self.license_state_transition, "")
                  ],
                  None
                  )

        self.server_url = None
        self.toolkit_initialized = False
        self.licensing_style = ""
        self.event_queue = []
        self.event_queue_time = 0.0
        self.first_event = True

        # The menu generation code makes use of the TK_RV_MODE_NAME environment
        # variable. Each menu item that is created in RV is associated with a
        # mode identified by its name. We need to make a note of our name so we
        # can add menu items for this mode later.

        os.environ["TK_RV_MODE_NAME"] = self._mode_name

    def init_and_process_events(self):
        self.initialize_toolkit()

    def pre_process_event(self, event):
        self.pre_process_event_pair(event.name(), event.contents())

    def pre_process_event_pair(self, name, contents):

        if self.licensing_style == "":
            self.licensing_style = rvc.readSettings("Licensing", "activeLicensingStyle", "")

        # sys.stderr.write("pre_process_event: lic style '%s' \n" % self.licensing_style)
        if self.licensing_style != "shotgun":
            # RV is not licensed via Shotgun, so notify user.
            sys.stderr.write("ERROR: Please authenticate RV with your Shotgun server and restart.\n")

        else:
            if self.toolkit_initialized:
                self.process_event(name, contents)

            else:
                if self.first_event:
                    msg = "Initializing Shotgun ..."
                    rve.displayFeedback2(msg, 2000.0)
                    self.first_event = False

                self.event_queue += [(name, contents)]
                self.event_queue_time = rvc.theTime()

                if rvc.licensingState() == 2:
                    self.init_and_process_events()

    def process_event(self, name, contents):

        sys.stderr.write("INFO: Processing event '%s' %g seconds after startup.\n" %
                         (name, rvc.theTime() - self.startup_time))

        if name == "external-gma-play-entity":
            self.external_gma_play_entity(name, contents)

        elif name == "external-gma-compare-entities":
            self.external_gma_compare_entities(name, contents)

        elif name == "external-sgtk-launch-app":
            self.external_launch_app(name, contents)
            rve.displayFeedback2("", 0.1)

        elif name == "external-launch-submit-tool":
            rvc.sendInternalEvent("launch-submit-tool", "")
            rve.displayFeedback2("", 0.1)

        elif name == "external-sgtk-initialize":
            rve.displayFeedback2("", 0.1)

    def process_queued_events(self):
        if self.event_queue:
            processed = []
            sys.stderr.write("INFO: Queued events waited %g seconds.\n" %
                             (rvc.theTime() - self.event_queue_time))
            for e in self.event_queue:
                if (e[0], e[1]) not in processed:
                    processed.append((e[0], e[1]))
                    self.process_event(e[0], e[1])

            self.event_queue = []

    #  This is dead code, but keep around in case we want to do this for
    #  debugging.
    #
    def play_entity_dialog_factory(self, entity):

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
                    rve.displayFeedback2("", 0.1)
                    log.error("could not convert '%s' to %s ID" % (idStr, entity))

        return dialog

    def server_check(self, contents):
        gma_data = json.loads(contents)
        if gma_data.has_key("server"):
            # sys.stderr.write("-------------------------------- event server '%s' vs '%s'\n" % (gma_data["server"], self.server_url))
            # check
            if urlparse.urlparse(gma_data["server"].lower()).netloc == urlparse.urlparse(
                    self.server_url.lower()).netloc:
                return True
            else:
                sys.stderr.write(
                    "ERROR: Server mismatch ('%s' vs '%s') Please authenticate RV with your Shotgun server and restart.\n" %
                    (gma_data["server"], self.server_url))
                rve.displayFeedback2("", 0.1)
                return False

        return True

    def external_gma_compare_entities(self, name, contents):
        if self.server_check(contents):
            rvc.sendInternalEvent("compare_ids_from_gma", contents)
            rvc.redraw()

    def external_gma_play_entity(self, name, contents):
        if self.server_check(contents):
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

    def external_launch_app(self, name, contents):
        if not self.server_check(contents):
            return

        app_data = json.loads(contents)

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

    def initialize_toolkit(self):
        try:
            # Clear the "stand-in" mode menu, and let the apps rebuild it
            modeMenu = [("SG Review", None)]
            rvc.defineModeMenu(self._modeName, modeMenu)

            startTime = rvc.theTime()
            bundle_cache_dir = os.path.join(sgtk_dist_dir(), "bundle_cache")

            core = os.path.join(bundle_cache_dir, "manual", "tk-core", "v1.3.0")
            core = os.environ.get("RV_TK_CORE") or core

            # append python path to get to the actual code
            core = os.path.join(core, "python")

            log.info("Looking for tk-core here: %s" % str(core))

            # now we can kick off sgtk
            sys.path.insert(0, core)
            sys.stderr.write(
                "INFO: Toolkit initialization: ready to import sgtk at %g sec.\n" % (rvc.theTime() - startTime))

            # import bootstrapper
            import sgtk
            sys.stderr.write(
                "INFO: Toolkit initialization: sgtk import complete at %g sec.\n" % (rvc.theTime() - startTime))

            # begin logging the toolkit log tree file
            sgtk.LogManager().initialize_base_file_handler("tk-rv")

            # import authentication code
            from sgtk_auth import get_toolkit_user

            # allow dev to override log level
            log_level = logging.WARNING
            if (os.environ.has_key("RV_TK_LOG_DEBUG")):
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
            sys.stderr.write(
                "INFO: Toolkit initialization: ToolkitManager complete at %g sec.\n" % (rvc.theTime() - startTime))

            # In disted code, by default, all TK code is read from the
            # 'bundle_cache' baked during the build process.
            mgr.bundle_cache_fallback_paths = [bundle_cache_dir]

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
                    version="v1.3.0",
                )

            # tell the bootstrap API that we don't want to
            # allow for overrides from Shotgun
            mgr.do_shotgun_config_lookup = False

            # define the entry point for this plugin in
            # order to sandbox it relative to other plugins
            mgr.entry_point = "rv_review"

            # Bootstrap the tk-rv engine into an empty context!
            def completed(e):
                self.process_queued_events()
                log.debug("tk-rv bootstrapping process completed")

            def failure(p, e):
                log.error("tk-rv bootstrapping process failed: %s" % (e))

            # mgr.bootstrap_engine("tk-rv")
            mgr.bootstrap_engine_async(
                "tk-rv",
                completed_callback=completed,
                failed_callback=failure,
            )

            log.debug("Bootstrapping process started")

            self.toolkit_initialized = True
            sys.stderr.write("INFO: Toolkit initialization took %g sec.\n" % (rvc.theTime() - startTime))

        except Exception, e:
            sys.stderr.write(
                "ERROR: Toolkit initialization failed.  Please authenticate RV with your Shotgun server and restart.\n" +
                "**********************************\n")
            traceback.print_exc(None, sys.stderr)
            sys.stderr.write(
                "**********************************\n")
            rve.displayFeedback2("", 0.1)
            # raise

    def get_default_rv_auth_session(self):
        """
        Returns a tuple with session details from rv authentication

        :returns: tuple (url, login, token) with shotgun url, login and session token
        """
        from pymu import MuSymbol
        rv.runtime.eval("require slutils;", [])
        # get session data from RV
        (last_session, sessions) = MuSymbol("slutils.retrieveSessionsData")()
        # grab the first three tokens out of the string
        (url, login, token) = last_session.split("|")[:3]
        # return (url, login, token)
        return url, login, token

    def get_help(self, event):
        rvc.openUrl("https://shotgunsoftware.zendesk.com/hc/en-us/articles/222840748")

    def launch_media_app(self, event):
        rvc.openUrl(self.server_url + "/page/media_center")

    def queue_launch_submit_tool(self, event):
        self.pre_process_event_pair("external-launch-submit-tool", "")

    def queue_launch_import_cut_app(self, event):
        (url, login, token) = self.get_default_rv_auth_session()
        self.server_url = url
        self.pre_process_event_pair('external-sgtk-launch-app',
                                    '{"protocol_version":1,"server":"%s","app":"tk-multi-importcut"}' % self.server_url)

    def initialize_shotgun(self, event):
        self.init_and_process_events()

    def launch_submit_tool(self):

        # Flag the session as "sgreview.submitInProgress" so JS submit tool
        # code can tell this is not Screening Room.
        #
        prop = "#Session.sgreview.submitInProgress"
        try:
            rvc.newProperty(prop, rvc.IntType, 1)
        except:
            pass
        rvc.setIntProperty(prop, [1], True)

        rv.runtime.eval("""
            {
                require shotgun_mode;
                require shotgun_review_app;
                require shotgun_upload;

                if (! shotgun_mode.localModeReady())
                {
                    //  Silence the mode first, then activate it.
                    //  shotgun_mode.silent = true;
                    shotgun_mode.createLocalMode();
                }
                if (! shotgun_review_app.localModeReady())
                {
                    //  Silence the mode first, then activate it.
                    //  shotgun_review_app.silent = true;
                    shotgun_review_app.createLocalMode();
                }
                if (! shotgun_upload.localModeReady())
                {
                    //  Silence the mode first, then activate it.
                    //  shotgun_upload.silent = true;
                    shotgun_upload.createLocalMode();
                }

                shotgun_review_app.theMode().internalLaunchSubmitTool();
            }
            """, [])

    def activate(self):
        """
        Activates the RV mode and bootstraps SGTK.
        """
        rvt.MinorMode.activate(self)

        self.licensing_style = rvc.readSettings("Licensing", "activeLicensingStyle", "")
        self.startup_licensing_state = rvc.licensingState()

    def license_state_transition(self, event):
        event.reject()

        if rvc.licensingState() == 2 and self.licensing_style == "shotgun":
            # If we can't reach Shotgun server, don't bother trying to initialize toolkit.
            if self.event_queue:
                if "Offline usage" in event.contents():
                    sys.stderr.write("INFO: Offline, so not initilizing Shotgun Toolkit\n")
                    msg = "Shotgun Offline ..."
                    rve.displayFeedback2(msg, 2.0)
                if not self.toolkit_initialized:
                    self.init_and_process_events()

            elif not "RV_SHOTGUN_NO_SG_REVIEW_MENU" in os.environ:
                # No events queued, so build Stand-in menu (IE don't initialize toolkit until we must)
                if "RV_LOAD_SG_REVIEW" in os.environ:
                    modeMenu = [("SG Review", [
                        ("_", None),
                        ("Get Help ...", self.get_help, None, lambda: rvc.UncheckedMenuState),

                        ("_", None),
                        ("Launch Media App", self.launch_media_app, None, lambda: rvc.UncheckedMenuState),

                        ("_", None),
                        ("Submit Tool", self.queue_launch_submit_tool, None, lambda: rvc.UncheckedMenuState),

                        ("_", None),
                        ("Import Cut", self.queue_launch_import_cut_app, None, lambda: rvc.UncheckedMenuState),

                        ("_", None),
                        ("Initialize Shotgun", self.initialize_shotgun, None, lambda: rvc.UncheckedMenuState),

                        ("_", None),
                        ]
                    )]
                    rvc.defineModeMenu(self._modeName, modeMenu)

                # We need url for some of these menu items
                (url, login, token) = self.get_default_rv_auth_session()
                self.server_url = url.encode("utf-8")

            self.initialize_shotgun(event)

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
    EscapedHtmlFormatter("%(levelname)s: %(name)s %(message)s")
)
log.addHandler(log_handler)