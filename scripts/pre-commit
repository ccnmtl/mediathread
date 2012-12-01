#!/bin/sh
# link me into your git hooks like so:
# ln -s `pwd`/scripts/pre-commit `pwd`/.git/hooks/pre-commit
branch="`git rev-parse --symbolic-full-name HEAD`"
echo "LAST_GIT_HEAD = \"`cat .git/$branch`\"" > release_id.py
git add release_id.py