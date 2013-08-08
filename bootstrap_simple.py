import os
import subprocess
import sys
import shutil
"""
this script is a simplified versionf of bootstrap.py
only extract javascript lib into media
"""
# install javascript libraries
pwd = os.path.abspath(os.path.dirname(__file__))
libs = [l.strip() for l in open(os.path.join(pwd, "requirements/js.txt"))]
jsdir = os.path.abspath(os.path.join(pwd, "media/js/"))
os.chdir(jsdir)
for lib in libs:
    ret = subprocess.call(["tar",
                           "xvzf",
                           "../../%s" % lib])
    if ret:
        exit(ret)
