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
    try:
        os.remove('lettuce.db')
    except:
        pass #database doesn't exist yet. that's ok.
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
        
@step(u'I am at the ([^"]*) page')
def i_am_at_the_name_page(step, name):
    if world.using_selenium:
        # Check the page title
        title = world.firefox.title
        assert title.find(name) > -1, "Page title is %s. Expected something like %s" % (title, name)
    
@step(u'I type "([^"]*)" for ([^"]*)')
def i_type_value_for_field(step, value, field):
    if world.using_selenium:
        selector = "input[name=%s]" % field
        input = world.firefox.find_element_by_css_selector(selector)
        assert input != None, "Cannot locate input field named %s" % field
        input.send_keys(value)
    
@step(u'I click the ([^"]*) button')
def i_click_the_value_button(step, value):
    if world.using_selenium:
        elt = find_button_by_value(value)
        assert elt, "Cannot locate button named %s" % value
        elt.click()
    
@step(u'I am logged in as ([^"]*)')
def i_am_logged_in_as_username(step, username):
    if world.using_selenium:
        world.firefox.get(django_url("/accounts/logout/"))
        world.firefox.get(django_url("accounts/login/?next=/"))
        username_field = world.firefox.find_element_by_id("id_username")
        password_field = world.firefox.find_element_by_id("id_password")
        form = world.firefox.find_element_by_name("login_local")
        username_field.send_keys(username)
        password_field.send_keys("test")
        form.submit()
        title = world.firefox.title
        assert username in world.firefox.page_source, world.firefox.page_source
    else:
        world.client.login(username=username,password='test')

@step(u'I am in the ([^"]*) class')
def i_am_in_the_coursename_class(step, coursename):
    if world.using_selenium:
        course_title = world.firefox.find_element_by_id("course_title")
        assert course_title.text.find(coursename) > -1, "Expected the %s class, but found the %s class" % (coursename, course_title.text)
        
@step(u'there is an? ([^"]*) button')
def there_is_a_value_button(step, value):
    elt = find_button_by_value(value)
    assert elt, "Cannot locate button named %s" % value

@step(u'there is not an? ([^"]*) button')
def there_is_not_a_value_button(step, value):
    elt = find_button_by_value(value)
    assert elt == None, "Found button named %s" % value
    
@step(u'I wait (\d+) second')
def then_i_wait_count_second(step, count):
    n = int(count)
    time.sleep(n)
    
    
# Local utility functions
def find_button_by_value(value):
    elts = world.firefox.find_elements_by_css_selector("input[type=submit]")
    for e in elts:
        if e.get_attribute("value") == value:
            return e
    
    elts = world.firefox.find_elements_by_css_selector("input[type=button]")
    for e in elts:
        if e.get_attribute("value") == value:
            return e
        
    # try the links too
    elts = world.firefox.find_elements_by_tag_name("a")
    for e in elts:
        if e.text and e.text.strip() == value:
            return e
        
    return None