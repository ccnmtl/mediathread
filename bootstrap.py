#!/usr/bin/env python
import argparse
import os
import shutil
import subprocess


parser = argparse.ArgumentParser()
parser.add_argument('-p', '--pypi', dest='pypi_url',
                    default='https://pypi.python.org/pypi',
                    help='Remote pypi repository')
args = parser.parse_args()

print "Pulling library resources from %s" % args.pypi_url

pwd = os.path.abspath(os.path.dirname(__file__))
vedir = os.path.abspath(os.path.join(pwd, "ve"))

if os.path.exists(vedir):
    shutil.rmtree(vedir)

virtualenv_support_dir = os.path.abspath(
    os.path.join(
        pwd, "requirements", "virtualenv_support"))

ret = subprocess.call(["python", "virtualenv.py",
                       "--extra-search-dir=%s" % virtualenv_support_dir,
                       "--never-download",
                       vedir])
if ret:
    exit(ret)

ret = subprocess.call(
    [os.path.join(vedir, 'bin', 'pip'), "install",
     "--index-url=http://pypi.ccnmtl.columbia.edu/",
     "wheel==0.21.0"])

if ret:
    exit(ret)

ret = subprocess.call(
    [os.path.join(vedir, 'bin', 'pip'), "install",
     "--use-wheel",
     "--index-url=%s" % args.pypi_url,
     "--requirement", os.path.join(pwd, "requirements.txt")])

if ret:
    exit(ret)

ret = subprocess.call(["python", "virtualenv.py", "--relocatable", vedir])
# --relocatable always complains about activate.csh, which we don't really
# care about. but it means we need to ignore its error messages

#install javascript libraries
libs = [l.strip() for l in open(os.path.join(pwd, "requirements/js.txt"))]
jsdir = os.path.abspath(os.path.join(pwd, "media/js/"))
os.chdir(jsdir)
for lib in libs:
    ret = subprocess.call(["tar",
                           "xvzf",
                           "../../%s" % lib])
    if ret:
        exit(ret)
