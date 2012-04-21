# -*- coding: utf-8 -*-
from lettuce.django import django_url
from lettuce import before, after, world, step
from django.test import client
import sys, os, time

import time
try:
    from lxml import html
    from selenium import webdriver
    from selenium.webdriver.firefox.firefox_profile import FirefoxProfile
    from selenium.common.exceptions import NoSuchElementException
    from selenium.webdriver.common.keys import Keys
    import selenium
except:
    pass

@before.harvest
def setup_database(variables):
    os.remove('lettuce.db')
    os.system("echo 'create table test(idx integer primary key);' | sqlite3 lettuce.db")
    os.system('./manage.py syncdb --settings=settings_test --noinput')
    os.system('./manage.py migrate --settings=settings_test --noinput')
    os.system('./manage.py loaddata mediathread_main/fixtures/sample_course.json --settings=settings_test')

@before.all
def setup_browser():
    ff_profile = FirefoxProfile() 
    ff_profile.set_preference("webdriver_enable_native_events", False) 
    world.firefox = webdriver.Firefox(ff_profile)
    world.client = client.Client()
    world.using_selenium = False

@after.all
def teardown_browser(total):
    world.firefox.quit()

@step(u'Using selenium')
def using_selenium(step):
    world.using_selenium = True

@step(u'Finished using selenium')
def finished_selenium(step):
    world.using_selenium = False

@before.each_scenario
def clear_selenium(step):
    world.using_selenium = False

@step(r'I access the url "(.*)"')
def access_url(step, url):
    if world.using_selenium:
        world.firefox.get(django_url(url))
    else:
        response = world.client.get(django_url(url))
        world.dom = html.fromstring(response.content)

@step(u'I am not logged in')
def i_am_not_logged_in(step):
    if world.using_selenium:
        world.firefox.get(django_url("/accounts/logout/"))
    else:
        world.client.logout()
        
@step(u'I log out')
def i_log_out(step):
    if world.using_selenium:
        world.firefox.get(django_url("/accounts/logout/"))
    else:
        response = world.client.get(django_url("/accounts/logout/"),follow=True)
        world.response = response
        world.dom = html.fromstring(response.content)
        
@step(u'Then I am at the "([^"]*)" page')
def then_i_am_at_the_name_page(step, name):
    # Check the page title
    title = world.firefox.title
    assert title.find(name) > -1, "Page title is %s. Expected something like %s" % (title, name)
    
@step(u'When I type "([^"]*)" for "([^"]*)"')
def when_i_type_value_for_field(step, value, field):
    selector = "input[name=%s]" % field
    input = world.firefox.find_element_by_css_selector(selector)
    assert input != None, "Cannot locate input field named %s" % field
    input.send_keys(value)
    
@step(u'When I click the "([^"]*)" button')
def when_i_click_the_name_button(step, name):
    elts = world.firefox.find_elements_by_css_selector("input[type=submit]")
    for e in elts:
        if e.get_attribute("value") == name:
            e.click()
            return
    
    elts = world.firefox.find_elements_by_css_selector("input[type=button]")
    for e in elts:
        if e.get_attribute("value") == name:
            e.click()
            return
        
    assert False, "Cannot locate button named %s" % name
    
@step(u'Then I wait (\d+) second')
def then_i_wait_count_second(step, count):
    n = int(count)
    time.sleep(n)
    
                