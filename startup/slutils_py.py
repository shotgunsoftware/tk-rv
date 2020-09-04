from pymu import MuSymbol
import rv


def defaultSession():
    rv.runtime.eval("require slutils;", [])
    (lastSession, sessions) = MuSymbol("slutils.retrieveSessionsData")()
    stuff = lastSession.split("|")
    # return (url, login, token)
    return (stuff[0], stuff[1], stuff[2])
