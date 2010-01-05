#! ../../ve/bin/python

x = open('data.json_tmpl').read()

import simplejson

import datetime
today = datetime.datetime.today()
yesterday = datetime.datetime.today() - datetime.timedelta(1)

x = x % locals()

y = open('data.json', 'w')
y.write(x)
