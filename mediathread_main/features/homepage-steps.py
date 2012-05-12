from lettuce.django import django_url
from lettuce import before, after, world, step
import sys, time

@step(u'There is an? ([^"]*) column')
def there_is_a_title_column(step, title):
    elts = world.firefox.find_elements_by_tag_name("h2")
    for e in elts:
        if e.text and e.text.strip() == title:
            return
        
    assert False, "Unable to find a column entitled %s" % title

@step(u'There is not an? ([^"]*) column')
def there_is_not_a_title_column(step, title):
    elts = world.firefox.find_elements_by_tag_name("h2")
    for e in elts:
        if e.text and e.text.strip() == title:
            assert False, "Found a column entitled %s" % title

@step(u'There is help for the ([^"]*) column')
def there_is_help_for_the_title_column(step, title):
    elts = world.firefox.find_elements_by_tag_name("h2")
    for e in elts:
        if e.text and e.text.strip() == title:
            help = e.parent.find_element_by_css_selector("div.helpblock.on")
            if help:
                return
        
    assert False, "No help found for %s" % title