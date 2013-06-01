#!/bin/sh
branch="`git rev-parse --symbolic-full-name HEAD`"
echo "LAST_GIT_HEAD = \"`cat .git/$branch`\"" > mediathread/release_id.py
git add mediathread/release_id.py