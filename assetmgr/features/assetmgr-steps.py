from lettuce.django import django_url
from lettuce import before, after, world, step
import sys, time
from selenium.webdriver import ActionChains
from selenium.webdriver.support.select import Select

@step(u'The item header is "([^"]*)"')
def the_item_header_is_name(step, name):
    if world.using_selenium:
        elt = world.browser.find_element_by_css_selector("div.asset-view-title")
        assert elt.text == name, "The title was %s. Expected %s" % (elt.text, name)