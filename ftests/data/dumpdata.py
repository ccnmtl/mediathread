#! ../../ve/bin/python

x = open('data.json').read()

import simplejson
x = simplejson.loads(x)

for i in x:
    if not i.has_key('fields'): continue
    if i['fields'].has_key('added'):
        if i['fields']['added'].startswith('2009-05-21'): i['fields']['added'] = "%(today)s"
        if i['fields']['added'].startswith('2009-05-20'): i['fields']['added'] = "%(yesterday)s"
    if i['fields'].has_key('modified'):
         if i['fields']['modified'].startswith('2009-05-21'): i['fields']['modified'] = "%(today)s"
         if i['fields']['modified'].startswith('2009-05-20'): i['fields']['modified'] = "%(yesterday)s"

from pprint import pprint
pprint(x)

y = open('data.json_tmpl', 'w')
simplejson.dump(x, y)
