[![Build Status](https://dev.azure.com/shotgun-ecosystem/Toolkit/_apis/build/status/shotgunsoftware.tk-rv?repoName=shotgunsoftware%2Ftk-rv&branchName=master)](https://dev.azure.com/shotgun-ecosystem/Toolkit/_build/latest?definitionId=99&repoName=shotgunsoftware%2Ftk-rv&branchName=master)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Linting](https://img.shields.io/badge/PEP8%20by-Hound%20CI-a873d1.svg)](https://houndci.com)

# tk-rv
Tweak implementation of a toolkit engine for RV.

To start:

Install shotgrid desktop to get tank.
Go where you installed your shotgrid root and find tank. Mine was in:
{SHOTGUN_INSTALL}/config
./tank updates

in the startup dir is the rv package install that

next and i dont know why, it wants to see the mode in:

~/Library/Application Support/RV/Python

so for ease of dev i do a symlink back to my dev version:
shotgun_toolkit_mode.py@ -> /Users/stewartb/git/tk-rv/startup/shotgun_toolkit_mode.py

go into rv prefs and make sure you're loading the package. if its working you should get a tk-rv menu.

QUESTIONS/NOTES:

there is a startup dir. that's where we make a rv mode class that becomes the package that lights this candle.
... ask Alan how we do this in a non package way? or is this what we want?

the python dir is for the actual tk-rv classes, in the style of tk-maya.

the engine stands alone and looks down for its groovy.

/shotgunlocal/config/config/core/shotgun.yml - your server settings....
