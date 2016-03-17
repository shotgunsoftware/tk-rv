#!/usr/bin/env bash
# Simple script to build a package in a local build directory
# The local package can then be used in rv with RV_SUPPORT_PATH=./build rv
mkdir -p ./build
rv_pkk="sgtk-1.0.rvpkg"
RV_SUPPORT_PATH=./build rm -f ${rv_pkk} && zip -D -j ${rv_pkk} src/PACKAGE src/sgtk_auth.py src/sgtk_bootstrap.py && rvpkg -add ./build -optin -force -install ${rv_pkk}