#!/usr/bin/env bash
##
# Update build files after making a production build
#

DEST_DIR="media/juxtapose/"
ORIG_DIR="$HOME/public_html/juxtapose/build/"

cp $ORIG_DIR/bundle.js $DEST_DIR/bundle-k.js
