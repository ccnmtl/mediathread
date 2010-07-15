#!/bin/bash

# For those with Git versions < 1.6.5, you need to do the submodule checkout recursion manually

## Presumably, you've done this already
#git clone git@github.com:ccnmtl/mediathread.git
#cd mediathread
git submodule init
#make our project checkouts
git submodule update

#now recurse into sherdjs
cd djangosherd/media/js/sherdjs/
git submodule init
git submodule update

