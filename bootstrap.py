#!/usr/bin/env python2.5
import os
import sys
import subprocess
import shutil

pwd = os.path.dirname(__file__)
vedir = os.path.join(pwd,"ve")

if os.path.exists(vedir):
    shutil.rmtree(vedir)

subprocess.call(["python2.5",os.path.join(pwd,"pip.py"),"install",
                 "-E",os.path.join(pwd,"ve"),
                 "--enable-site-packages",
                 "--requirement",os.path.join(pwd,"requirements/apps.txt")])

