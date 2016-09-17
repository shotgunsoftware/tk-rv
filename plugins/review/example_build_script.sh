#!/bin/bash

#############################################
# example build script for plugin
# this script will do the following:
#
# 1. download the latest toolkit core (master branch)
# 2. download the latest rv plugin
# 3. run the build script
#
# NOTE: The script needs to connect to the toolkit app store
#       you need to set it up with script credentials.

# create temp folder
build_folder=`mktemp -d`
echo "Building in temp folder $build_folder"
cd $build_folder

echo "Downloading core..."
git clone git@github.com:shotgunsoftware/tk-core.git

echo "Downloading RV plugin source code..."
# probably need to have ssh credentials set up here to avoid auth prompt
git clone git@github.com:shotgunsoftware/tk-rv.git

######################################################################
# NOTE >>>> checking out the dev branch
# once the baked build branch has been merged with master
# this wont be needed
cd tk-rv
git checkout 36020_baked_build
cd ..
######################################################################

echo "Building plugin"
cd tk-core/developer
# using script name/script key for auth
python build_plugin.py ../../tk-rv/plugins/review ../../rv_build -s https://MYSITE.shotgunstudio.com -n SCRIPTNAME -k SCRIPTKEY

echo "Build complete in $build_folder/rv_build"
echo ""
echo "Now move the bundle_cache and python folders into RV_ROOT/src/python/sgtk"
echo "and *.py into RV_ROOT/Plugins/Python"
echo ""
