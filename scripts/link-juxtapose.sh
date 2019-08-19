#!/usr/bin/env bash
##
# Set up symlinks for juxtapose development
#

DEST_DIR="media/juxtapose/"
ORIG_DIR="$HOME/public_html/juxtapose/build/"

rm $DEST_DIR/bundle-k.js

ln -s $ORIG_DIR/bundle.js $DEST_DIR/bundle-k.js
