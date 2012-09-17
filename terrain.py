# -*- coding: utf-8 -*-
from lettuce.django import django_url
from lettuce import before, after, world, step
from django.test import client
import sys, os, time
from selenium.webdriver.common.keys import Keys
import selenium.webdriver.support.ui as ui
from mediathread.projects.models import Project
from mediathread.structuredcollaboration.models import Collaboration
from mediathread.structuredcollaboration.models import CollaborationPolicyRecord

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

@before.each_feature
def setup_database(variables):
    try:
        os.remove('lettuce.db')
    except:
        pass #database doesn't exist yet. that's ok.
    os.system("echo 'create table test(idx integer primary key);' | sqlite3 lettuce.db > /dev/null")
    os.system('./manage.py syncdb --settings=settings_test --noinput > /dev/null')
    os.system('./manage.py migrate --settings=settings_test --noinput > /dev/null')
    os.system("echo 'delete from django_content_type;' | sqlite3 lettuce.db > /dev/null")
    os.system('./manage.py loaddata mediathread_main/fixtures/sample_course.json --settings=settings_test > /dev/null')
    time.sleep(2)

@before.all
def setup_browser():
    ff_profile = FirefoxProfile() 
    ff_profile.set_preference("webdriver_enable_native_events", False) 
    world.firefox = webdriver.Firefox(ff_profile)
    world.client = client.Client()
    world.using_selenium = False
    
    # Make the browser size at least 1024x768
    world.firefox.execute_script("window.moveTo(0, 1); window.resizeTo(1024, 768);");
    
    # stash
    world.memory = {}
    
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
    
    Project.objects.all().delete()
    Collaboration.objects.exclude(title="Sample Course").exclude(title="Alternate Course").delete()
    CollaborationPolicyRecord.objects.all().delete()
    os.system("echo 'delete from projects_project_participants;' | sqlite3 lettuce.db > /dev/null")
    os.system("echo 'delete from projects_projectversion;' | sqlite3 lettuce.db > /dev/null")
    os.system("echo 'delete from threadedcomments_comment;' | sqlite3 lettuce.db > /dev/null")
    os.system("echo 'delete from django_comments;' | sqlite3 lettuce.db > /dev/null")
    os.system("echo 'delete from django_comment_flags;' | sqlite3 lettuce.db > /dev/null")
    
@step(r'I access the url "(.*)"')
def access_url(step, url):
    if world.using_selenium:
        world.firefox.get(django_url(url))
    else:
        response = world.client.get(django_url(url))
        world.dom = html.fromstring(response.content)
    
@step(u'Given the ([^"]*) workspace is loaded')
def given_the_name_workspace_is_loaded(step, name):
    if name == "composition":
        elt = ""
    elif name == "assignment":
        elt == ""
    elif name == "discussion":
        elt = ""
    elif name == "home":
        elt = "loaded"
    else:
        assert False, "No selector configured for %s" % name
        
    #wait = new WebDriverWait(d, TimeSpan.FromSeconds(5));
    #    var element = wait.Until(driver => driver.FindElement(By.Id("Hobbies")));
        
    wait = ui.WebDriverWait(world.firefox, 10)
    wait.until(ui.ExpectedConditions.visibilityOf(By.id(elt)))
        
        
@step(u'my browser resolution is ([^"]*) x ([^"]*)')
def my_browser_resolution_is_width_x_height(step, width, height):
    cmd = "window.moveTo(0, 1); window.resizeTo(%s, %s);" % (width, height)
    world.firefox.execute_script(cmd);
        
        
@step(u'I am ([^"]*) in ([^"]*)')
def i_am_username_in_course(step, username, course):
    if world.using_selenium:
        world.firefox.get(django_url("/accounts/logout/"))
        world.firefox.get(django_url("accounts/login/?next=/"))
        time.sleep(1)
        username_field = world.firefox.find_element_by_id("id_username")
        password_field = world.firefox.find_element_by_id("id_password")
        form = world.firefox.find_element_by_name("login_local")
        username_field.send_keys(username)
        password_field.send_keys("test")
        form.submit()
        title = world.firefox.title
        assert username in world.firefox.page_source, world.firefox.page_source
        
        step.given('I access the url "/"')
        step.given('I am in the %s class' % course)
        step.given('I am at the Home page')
    else:
        world.client.login(username=username,password='test')

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
        try:
            title = world.firefox.title
            assert title.find(name) > -1, "Page title is %s. Expected something like %s" % (title, name)
        except:
            time.sleep(1)
            title = world.firefox.title
            assert title.find(name) > -1, "Page title is %s. Expected something like %s" % (title, name)
            
@step(u'there is a sample assignment')            
def there_is_a_sample_assignment(step):
    os.system('./manage.py loaddata mediathread_main/fixtures/sample_assignment.json --settings=settings_test > /dev/null')
    time.sleep(2)

@step(u'there is a sample assignment and response')            
def there_is_a_sample_assignment_and_response(step):
    os.system('./manage.py loaddata mediathread_main/fixtures/sample_assignment_and_response.json --settings=settings_test > /dev/null')
    time.sleep(2)
    
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
        
@step(u'there is not an? "([^"]*)" link')
def there_is_not_a_text_link(step, text):
    if not world.using_selenium:
        for a in world.dom.cssselect("a"):
            if a.text:
                if text.strip().lower() in a.text.strip().lower():
                    href = a.attrib['href']
                    response = world.client.get(django_url(href))
                    world.dom = html.fromstring(response.content)
                    assert False, "found the '%s' link" % text
    else:
        try:
            link = world.firefox.find_element_by_partial_link_text(text)
            assert False, "found the '%s' link" % text
        except:
            pass # expected             
        
@step(u'there is an? "([^"]*)" link')
def there_is_a_text_link(step, text):
    if not world.using_selenium:
        for a in world.dom.cssselect("a"):
            if a.text:
                if text.strip().lower() in a.text.strip().lower():
                    href = a.attrib['href']
                    response = world.client.get(django_url(href))
                    world.dom = html.fromstring(response.content)
                    return
        assert False, "could not find the '%s' link" % text
    else:
        try:
            link = world.firefox.find_element_by_partial_link_text(text)
            assert link.is_displayed()
        except:
            try:
                time.sleep(2)
                link = world.firefox.find_element_by_partial_link_text(text)
                assert link.is_displayed()
            except:
                world.firefox.get_screenshot_as_file("/tmp/selenium.png")
                assert False, "Cannot find link %s" % text   
        
        
@step(u'I click the "([^"]*)" link')
def i_click_the_link(step, text):
    if not world.using_selenium:
        for a in world.dom.cssselect("a"):
            if a.text:
                if text.strip().lower() in a.text.strip().lower():
                    href = a.attrib['href']
                    response = world.client.get(django_url(href))
                    world.dom = html.fromstring(response.content)
                    return
        assert False, "could not find the '%s' link" % text
    else:
        try:
            link = world.firefox.find_element_by_partial_link_text(text)
            assert link.is_displayed()
            link.click()
        except:
            try:
                time.sleep(1)
                link = world.firefox.find_element_by_partial_link_text(text)
                assert link.is_displayed()
                link.click()
            except:
                world.firefox.get_screenshot_as_file("/tmp/selenium.png")
                assert False, link.location      

@step(u'I am in the ([^"]*) class')
def i_am_in_the_coursename_class(step, coursename):
    if world.using_selenium:
        try:
            course_title = world.firefox.find_element_by_id("course_title")
        except:
            time.sleep(1)
            course_title = world.firefox.find_element_by_id("course_title")
            
        assert course_title.text.find(coursename) > -1, "Expected the %s class, but found the %s class" % (coursename, course_title.text)
        
@step(u'there is an? ([^"]*) button')
def there_is_a_value_button(step, value):
    try:
        elt = find_button_by_value(value)
        assert elt, "Cannot locate button named %s" % value
    except:
        time.sleep(1)
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
    
@step(u'I see "([^"]*)"')
def i_see_text(step, text):
    try:
        assert text in world.firefox.page_source, world.firefox.page_source
    except:
        time.sleep(1)
        assert text in world.firefox.page_source, "I did not see %s in this page" % text
    
@step(u'I do not see "([^"]*)"')
def i_do_not_see_text(step, text):
    assert text not in world.firefox.page_source, world.firefox.page_source
    
@step(u'I cancel an alert dialog')
def i_cancel_an_alert_dialog(step):
    time.sleep(1)
    alert = world.firefox.switch_to_alert()
    alert.dismiss()
    time.sleep(1)    

@step(u'I ok an alert dialog')
def i_ok_an_alert_dialog(step):
    time.sleep(1)
    alert = world.firefox.switch_to_alert()
    alert.accept()
    time.sleep(1)
    
@step(u'I open the user settings menu')
def i_open_the_user_settings_menu(step):
    elt = world.firefox.find_element_by_css_selector("li.settings")
    elt.click()
    
@step(u'there is an? ([^"]*) column')
def there_is_a_title_column(step, title):
    elts = world.firefox.find_elements_by_tag_name("h2")
    if len(elts) < 1:
        time.sleep(1)
        elts = world.firefox.find_elements_by_tag_name("h2")
    
    for e in elts:
        if e.text and e.text.strip().lower().find(title.lower()) > -1:
            return
        
    assert False, "Unable to find a column entitled %s" % title

@step(u'there is not an? ([^"]*) column')
def there_is_not_a_title_column(step, title):
    elts = world.firefox.find_elements_by_tag_name("h2")
    for e in elts:
        if e.text and e.text.strip().lower().startswith(title.lower()):
            assert False, "Found a column entitled %s" % title

@step(u'there is help for the ([^"]*) column')
def there_is_help_for_the_title_column(step, title):
    elts = world.firefox.find_elements_by_tag_name("h2")
    for e in elts:
        if e.text and e.text.strip().lower().startswith(title.lower()):
            help = e.parent.find_element_by_css_selector("div.helpblock.on")
            return
        
    assert False, "No help found for %s" % title    
    
@step(u'there is no help for the ([^"]*) column')
def there_is_no_help_for_the_title_column(step, title):
    elts = world.firefox.find_elements_by_tag_name("h2")
    for e in elts:
        if e.text and e.text.strip().lower().startswith(title.lower()):
            try:
                help = e.parent.find_element_by_css_selector("div.helpblock.on")
                assert False, "Help found for %s" % title
            except:
                return # Expected outcome
    
@step(u'I\'m told ([^"]*)')
def i_m_told_text(step, text):
    alert = world.firefox.switch_to_alert()
    assert alert.text.startswith(text), "Alert text invalid: %s" % alert.text
    alert.accept()
    
 
@step(u'the most recent notification is "([^"]*)"')
def the_most_recent_notification_is_text(step, text):
    try:
        list = world.firefox.find_element_by_id("parent-clumper")
    except:
        time.sleep(1)
        list = world.firefox.find_element_by_id("parent-clumper")
    
    elts = list.find_elements_by_css_selector("div.asset_title")
    assert len(elts) > 0, "Found 0 notifications. Expected at least one."
    
    link = elts[0].find_element_by_tag_name("a")
    assert link != None, "Found no notification links. Expected at least one"
    
    assert link.text.strip() == text, "Notification text is [%s]. Expected [%s]" % (link.text.strip(), text)
    
@step(u'I select "([^"]*)" as the owner in the ([^"]*) column')
def i_select_name_as_the_owner_in_the_title_column(step, name, title):
    column = get_column(title)
    if not column:
        time.sleep(1)
        column = get_column(title)
        
    assert column, "Unable to find a column entitled %s" % title

    try:
        menu = column.find_element_by_css_selector("div.switcher_collection_chooser")
    except:
        time.sleep(2)
        menu = column.find_element_by_css_selector("div.switcher_collection_chooser")

    assert menu, 'Unable to find the owner menu'
    
    menu.find_element_by_css_selector("a.switcher-top").click()
    
    owners = menu.find_elements_by_css_selector("a.switcher-choice.owner")
    for o in owners:
        if o.text.find(name) > -1:
            o.click()
            return
        
    assert False, "Unable to find owner %s" % name
    
@step(u'the owner is "([^"]*)" in the ([^"]*) column')    
def the_owner_is_name_in_the_title_column(step, name, title):
    time.sleep(2)
    column = get_column(title)
    assert column, "Unable to find a column entitled %s" % title
    
    menu = column.find_element_by_css_selector("div.switcher_collection_chooser")
    owner = menu.find_element_by_css_selector("a.switcher-top span.title")        
    assert owner.text == name, "Expected owner title to be %s. Actually %s" % (name, owner.text)    
    
@step(u'the collection panel has a "([^"]*)" item')
def the_collection_panel_has_a_title_item(step, title):
    panel = get_column('collection')
    assert panel, "Cannot find the collection panel"

    items = panel.find_elements_by_css_selector('div.gallery-item-homepage')
    for i in items:
        elt = i.find_element_by_css_selector('a.asset-title-link')
        if elt.text == title:
            return
    
    assert False, "Unable to find an item named %s in the collection panel" % title
    
@step(u'the collection panel has no "([^"]*)" item')
def the_collection_panel_has_no_title_item(step, title):
    panel = get_column('collection')
    if not panel:
        time.sleep(2)
        panel = get_column('collection')
    assert panel, "Cannot find the collection panel"
    
    items = panel.find_elements_by_css_selector('div.gallery-item-homepage')
    for i in items:
        elt = i.find_element_by_css_selector('a.asset-title-link')
        if elt.text == title:
            assert False, "Found an item named %s in the collection panel" % title
    
    assert True, "Unable to find the %s item in the collection panel" % title    
    
@step(u'the "([^"]*)" item has a note "([^"]*)"')
def the_title_item_has_a_note_text(step, title, text):
    panel = get_column('collection')
    assert panel, "Cannot find the collection panel"
    
    items = panel.find_elements_by_css_selector('div.gallery-item-homepage')
    for i in items:
        elt = i.find_element_by_css_selector('a.asset-title-link')
        if elt.text == title:
            note = i.find_element_by_css_selector('li.annotation-global-body span.metadata-value')
            assert note, "Unable to find a note for the %s item" % title
            assert note.text == text, "The item note reads %s. Expected %s" % (note.text, text)
            return
            
    assert False, "Unable to find an item named %s in the collection panel" % title
    
@step(u'the "([^"]*)" item has ([^"]*) selections, ([^"]*) by me')
def the_title_item_has_a_total_selections_count_by_me(step, title, total, count):
    panel = get_column('collection')
    assert panel, "Cannot find the collection panel"
    
    items = panel.find_elements_by_css_selector('div.gallery-item-homepage')
    for i in items:
        elt = i.find_element_by_css_selector('a.asset-title-link')
        if elt.text == title:
            item_total = i.find_element_by_css_selector('span.item-annotation-count-total')
            assert item_total.text == total, "The item selection total is %s. Expected %s" % (item_total.text, total)
            
            my_count = i.find_element_by_css_selector('span.item-annotation-count-user')
            assert my_count.text == count, "The user item selection count is %s. Expected %s" % (my_count.text, count)
            
            return
            
    assert False, "Unable to find an item named %s in the collection panel" % title
    
       
    
@step(u'the "([^"]*)" item has a tag "([^"]*)"')
def the_title_item_has_a_tag_text(step, title, text):
    panel = get_column('collection')
    assert panel, "Cannot find the collection panel"
    
    items = panel.find_elements_by_css_selector('div.gallery-item-homepage')
    for i in items:
        elt = i.find_element_by_css_selector('a.asset-title-link')
        if elt.text == title:
            tags = i.find_elements_by_css_selector('li.annotation-global-tags span.metadata-value a.switcher-choice')
            for t in tags:
                if t.text == text:
                    return 
            assert tag, "Unable to find a tag for the %s item" % title
            return
            
    assert False, "Unable to find an item named %s in the collection panel" % title
    
    
@step(u'the "([^"]*)" item has a selection "([^"]*)"')
def the_title_item_has_a_selection_seltitle(step, title, seltitle):
    panel = get_column('collection')
    assert panel, "Cannot find the collection panel"
    
    items = panel.find_elements_by_css_selector('div.gallery-item-homepage')
    for i in items:
        elt = i.find_element_by_css_selector('a.asset-title-link')
        if elt.text == title:
            selection = i.find_element_by_css_selector('td.selection-meta div.metadata-container a.materialCitationLink')
            assert selection, "Unable to find the %s selection" % seltitle
            assert selection.text == seltitle, "Selection title is %s. Expected %s" % (selection.text, seltitle)
            return
    
    assert False, "Unable to find an item named %s in the collection panel" % title
    
@step(u'the "([^"]*)" item has no selections')
def the_title_item_has_no_selections(step, title):
    panel = get_column('collection')
    assert panel, "Cannot find the collection panel"
    
    items = panel.find_elements_by_css_selector('div.gallery-item-homepage')
    for i in items:
        elt = i.find_element_by_css_selector('a.asset-title-link')
        if elt.text == title:
            try:
                selections = i.find_elements_by_css_selector('td.selection-meta div.metadata-container a.materialCitationLink')
                assert False, "Item %s has %s selections" % (title, len(selections))
            except:
                return 
    
    assert False, "Unable to find an item named %s in the collection panel" % title
    
@step(u'the "([^"]*)" item has no notes')
def the_title_item_has_no_notes(step, title):
    panel = get_column('collection')
    assert panel, "Cannot find the collection panel"
    
    items = panel.find_elements_by_css_selector('div.gallery-item-homepage')
    for i in items:
        elt = i.find_element_by_css_selector('a.asset-title-link')
        if elt.text == title:
            try:
                note = i.find_element_by_css_selector('li.annotation-global-body span.metadata-value')
                assert False, "Item %s has notes" % title
            except:
                return
            
    assert False, "Unable to find an item named %s in the collection panel" % title
    
@step(u'the "([^"]*)" item has no tags')
def the_title_item_has_no_tags(step, title):
    panel = get_column('collection')
    assert panel, "Cannot find the collection panel"
    
    items = panel.find_elements_by_css_selector('div.gallery-item-homepage')
    for i in items:
        elt = i.find_element_by_css_selector('a.asset-title-link')
        if elt.text == title:
            try:
                tag = i.find_element_by_css_selector('li.annotation-global-tags span.metadata-value a.switcher-choice')
                assert False, "Item %s has tags" % title
            except:
                return
            
    assert False, "Unable to find an item named %s in the collection panel" % title
    
    
@step(u'the "([^"]*)" selection has a note "([^"]*)"')
def the_seltitle_selection_has_a_note_text(step, seltitle, text):
    panel = get_column('collection')
    assert panel, "Cannot find the collection panel"
    
    selections = panel.find_elements_by_css_selector('td.selection-meta')
    for s in selections:
         title = s.find_element_by_css_selector('div.metadata-container a.materialCitationLink')
         if title and title.text == seltitle:
             note = s.find_element_by_css_selector('div.annotation-notes span.metadata-value')
             assert note, "Unable to find a note for the %s selection" % seltitle
             assert note.text == text, "The %s note reads %s. Expected %s" % (seltitle, note.text, text) 
             return
        
    assert False, "Unable to find a selection named %s in the collection panel" % seltitle
    
    
@step(u'the "([^"]*)" selection has a tag "([^"]*)"')
def the_seltitle_selection_has_a_tag_text(step, seltitle, text):
    panel = get_column('collection')
    assert panel, "Cannot find the collection panel"
    
    selections = panel.find_elements_by_css_selector('td.selection-meta')
    for s in selections:
         title = s.find_element_by_css_selector('div.metadata-container a.materialCitationLink')
         if title and title.text == seltitle:
             tags = s.find_elements_by_css_selector('div.annotation-tags span.metadata-value a.switcher-choice')
             for t in tags:
                 if t.text == text:
                     return
             assert tag, "Unable to find a tag for the %s selection" % seltitle
             return
        
    assert False, "Unable to find a selection named %s in the collection panel" % seltitle
    
@step(u'the "([^"]*)" item has an? ([^"]*) icon')
def the_title_item_has_a_type_icon(step, title, type):
    time.sleep(1)
    items = world.firefox.find_elements_by_css_selector("div.gallery-item-homepage");
    for item in items:
        try:
            link = item.find_element_by_partial_link_text(title)
        except:
            continue
            
        try:
            icon = item.find_element_by_css_selector("a.%s-asset" % type)
            return # found the link & the icon
        except: 
            assert False, "Item %s does not have a %s icon." % (title, type)
     
    assert False, "Unable to find the %s item" % title   
    
@step(u'the "([^"]*)" item has no ([^"]*) icon')
def the_title_item_has_no_type_icon(step, title, type):
    time.sleep(1)
    items = world.firefox.find_elements_by_css_selector("div.gallery-item-homepage");
    for item in items:
        try:
            link = item.find_element_by_partial_link_text(title)
        except:
            continue
            
        try:
            icon = item.find_element_by_css_selector("a.%s-asset" % type)
            assert False, "Item %s has a %s icon." % (title, type)
        except: 
            assert True, "Item %s does not have a %s icon" % (title, type)
            return
     
    assert False, "Unable to find the %s item" % title       
            
@step(u'I click the "([^"]*)" item ([^"]*) icon')
def i_click_the_title_item_type_icon(step, title, type):
    time.sleep(1)
    items = world.firefox.find_elements_by_css_selector("div.gallery-item-homepage");
    for item in items:
        try:
            link = item.find_element_by_partial_link_text(title)
        except:
            continue
            
        try:
            if type == "delete":
                icon = item.find_element_by_css_selector(".%s_icon" % type)
            else:
                icon = item.find_element_by_css_selector("a.%s-asset" % type)
                
            icon.click()
            return # found the link & the icon
        except:
            assert False, "Item %s does not have a %s icon." % (title, type)
     
    assert False, "Unable to find the %s item" % title   
    
@step(u'I can filter by "([^"]*)" in the ([^"]*) column')    
def i_can_filter_by_tag_in_the_title_column(step, tag, title):
    column = get_column(title)
    if not column:
        time.sleep(1)
        column = get_column(title)
        
    assert column, "Unable to find a column entitled %s" % title
    
    filter_menu = column.find_element_by_css_selector("div.switcher.collection-filter a.switcher-top")
    filter_menu.click()
    
    tags = column.find_elements_by_css_selector("div.switcher.collection-filter a.switcher-choice.filterbytag")
        
    for t in tags:
        if t.text == tag:
            filter_menu.click()
            return
        
    filter_menu.click()
    assert False, "Unable to filter by %s tag" % tag
    
@step(u'I filter by "([^"]*)" in the ([^"]*) column')    
def i_filter_by_tag_in_the_title_column(step, tag, title):
    column = get_column(title)
    if not column:
        time.sleep(1)
        column = get_column(title)
        
    assert column, "Unable to find a column entitled %s" % title
    
    filter_menu = column.find_element_by_css_selector("div.switcher.collection-filter a.switcher-top")
    filter_menu.click()
    
    tags = column.find_elements_by_css_selector("div.switcher.collection-filter a.switcher-choice.filterbytag")
        
    for t in tags:
        if t.text == tag:
            t.click()
            time.sleep(2)
            return
        
    filter_menu.click()
    assert False, "Unable to filter by %s tag" % tag  
    
@step(u'I clear the filter in the ([^"]*) column')
def i_clear_the_filter_in_the_title_column(step, title): 
    column = get_column(title)
    if not column:
        time.sleep(1)
        column = get_column(title) 
        
    assert column, "Unable to find a column entitled %s" % title
    
    elt = column.find_element_by_css_selector("a.switcher-choice.remove")
    elt.click()
    time.sleep(2)    
    
@step(u'Given publish to world is ([^"]*)')
def given_publish_to_world_is_value(step, value):
    if world.using_selenium:
        world.firefox.get(django_url("/dashboard/settings/"))
        
        if value == "enabled":
            elt = world.firefox.find_element_by_id('allow_public_compositions_yes')
            elt.click();
        else:
            elt = world.firefox.find_element_by_id('allow_public_compositions_no')
            elt.click();
        
        elt = world.firefox.find_element_by_id("allow_public_compositions_submit")
        if elt: 
            elt.click()
            alert = world.firefox.switch_to_alert()
            alert.accept()
            
            world.firefox.get(django_url("/"))
            
@step(u'Then publish to world is ([^"]*)')
def then_publish_to_world_is_value(step, value):
    if value == 'enabled':
        elt = world.firefox.find_element_by_id('allow_public_compositions_yes')
    else:
        elt = world.firefox.find_element_by_id('allow_public_compositions_no')
    
    assert elt.get_attribute('checked'), "The checked attribute was %s" % elt.get_attribute("checked")                
    
@step(u'I cannot filter by "([^"]*)" in the ([^"]*) column')    
def i_cannot_filter_by_tag_in_the_title_column(step, tag, title):
    column = get_column(title)
    if not column:
        time.sleep(1)
        column = get_column(title)
        
    assert column, "Unable to find a column entitled %s" % title
    
    filter_menu = column.find_element_by_css_selector("div.switcher.collection-filter")
    assert filter_menu
    filter_menu.click()
    
    try:
        tags = filter_menu.find_element_by_css_selector("a.switcher-choice.filterbytag")
        for t in tags:
            if t.text == tag:
                assert False, "Found %s tag" % tag
    except:
        # pass - there may be no tags
        return
    
@step(u'The "([^"]*)" project has no delete icon')
def the_title_project_has_no_delete_icon(step, title):
    time.sleep(1)
    link = world.firefox.find_element_by_partial_link_text(title)
    try:
        link.parent.find_element_by_css_selector(".delete_icon")
        assert False, "%s does have a delete icon" % title
    except:
        assert True, "Item does not have a delete icon"

@step(u'The "([^"]*)" project has a delete icon')
def the_title_project_has_a_delete_icon(step, title):
    try:
        link = world.firefox.find_element_by_partial_link_text(title)
    except:
        time.sleep(2)
        link = world.firefox.find_element_by_partial_link_text(title)
    
    try:
        link.parent.find_element_by_css_selector(".delete_icon")
    except:
        time.sleep(1)
        link.parent.find_element_by_css_selector(".delete_icon")
        
@step(u'I click the "([^"]*)" project delete icon')
def i_click_the_title_project_delete_icon(step, title):
    try:
        link = world.firefox.find_element_by_partial_link_text(title)
    except:
        time.sleep(1)
        link = world.firefox.find_element_by_partial_link_text(title)
    
    try:
        img = link.parent.find_element_by_css_selector(".delete_icon")
    except:
        time.sleep(1)
        img = link.parent.find_element_by_css_selector(".delete_icon")
        
    img.click()      
        
@step(u'the instructor panel has ([0-9][0-9]?) projects? named "([^"]*)"')
def the_instructor_panel_has_count_projects_named_title(step, count, title):
    elts = world.firefox.find_elements_by_css_selector("ul.instructor-list li")
    n = 0
    for e in elts:
        a = e.find_element_by_css_selector("a")
        if a.text == title:
            n += 1
    assert n == int(count), "The instructor panel had %s projects named %s. Expected %s"  % (n, title, count)
    
@step(u'the classwork panel has ([0-9][0-9]?) projects named "([^"]*)"')
def the_classwork_panel_has_count_projects_named_title(step, count, title):
    elts = world.firefox.find_elements_by_css_selector("li.projectlist")
    if len(elts) < 1:
        time.sleep(1)
        elts = world.firefox.find_elements_by_css_selector("li.projectlist")
        
    n = 0
    for e in elts:
        a = e.find_element_by_css_selector("a.asset_title")
        if a.text == title:
            n += 1
    assert n == int(count), "There are %s projects named %s. Expected %s"  % (n, title, count) 
    
@step(u'there is an? ([^"]*) ([^"]*) panel')
def there_is_a_state_name_panel(step, state, name):
    """
    Keyword arguments:
    state -- open, closed
    name -- composition, assignment, discussion, collection 

    """
    try:
        panel = world.firefox.find_element_by_css_selector("td.panel-container.%s.%s" % (state.lower(), name.lower()))
    except:
        time.sleep(1)
        panel = world.firefox.find_element_by_css_selector("td.panel-container.%s.%s" % (state.lower(), name.lower()))
    assert panel != None, "Can't find panel named %s" % panel
    
@step(u'I call the ([^"]*) "([^"]*)"')
def i_call_the_panel_title(step, panel, title):
    try:
        panel = world.firefox.find_element_by_css_selector("td.panel-container.open.%s" % panel.lower())
    except:
        time.sleep(1)
        panel = world.firefox.find_element_by_css_selector("td.panel-container.open.%s" % panel.lower())
    assert panel != None, "Can't find panel named %s" % panel
    
    input = panel.find_element_by_name("title")
    input.clear()
    input.send_keys(title)

@step(u'I write some text for the ([^"]*)')
def i_write_some_text_for_the_panel(step, panel):
    panel = world.firefox.find_element_by_css_selector("td.panel-container.open.%s" % panel.lower())
    assert panel != None, "Can't find panel named %s" % panel
    
    frame = panel.find_element_by_tag_name("iframe")
    world.firefox.switch_to_frame(frame)
    input = world.firefox.find_element_by_class_name("mceContentBody")
    input.send_keys("""The Columbia Center for New Teaching and Learning was (CCNMTL)
                    was founded at Columbia University in 1999 to enhance teaching and
                    learning through the purposeful use of new media and technology""")
    
    world.firefox.switch_to_default_content()       
    
@step(u'there is an? ([^"]*) "([^"]*)" project by ([^"]*)')
def there_is_a_status_title_project_by_author(step, status, title, author):
    elts = world.firefox.find_elements_by_css_selector("li.projectlist")
    if len(elts) < 1:
        time.sleep(1)
        elts = world.firefox.find_elements_by_css_selector("li.projectlist")
    assert len(elts) > 0, "Expected to find at least 1 project. Instead there are none"
    
    assignment = False
    for e in elts:
        try:
            title_elt = e.find_element_by_css_selector("a.asset_title.type-project")
        except:
            title_elt = e.find_element_by_css_selector("a.asset_title.type-assignment")
            assignment = True
            
        if title_elt.text.strip() == title:
            if not assignment:
                # author
                author_elt = e.find_element_by_css_selector("span.metadata-value-author")
                msg = "%s author is [%s]. Expected [%s]." % (title, author_elt.text.strip(), author)
                assert author_elt.text.strip() == author, msg
                
            # status            
            status_elt = e.find_element_by_css_selector("span.metadata-value-status")
            msg = "%s status starts with [%s]. Expected [%s]" % (title, status_elt.text.strip().lower(), status)
            assert status_elt.text.strip().lower().startswith(status), msg 
            
            return
            
    assert False, "Unable to find project named %s" % title
    
@step(u'The ([^"]*) title is "([^"]*)"')
def the_panel_title_is_value(step, panel, value):
    try:
        panel = world.firefox.find_element_by_css_selector("td.panel-container.open.%s" % panel.lower())
    except:
        time.sleep(1)
        panel = world.firefox.find_element_by_css_selector("td.panel-container.open.%s" % panel.lower())
    assert panel != None, "Can't find panel named %s" % panel
    
    h1 = panel.find_element_by_css_selector("h1.project-title")
    assert h1.text.strip() == value, "Expected %s title %s. Found %s" % (panel, value, h1.text.strip())
    
    
@step(u'i save the changes')
def i_save_the_changes(step):
    elts = world.firefox.find_elements_by_tag_name("button")
    for e in elts:
        if e.get_attribute("type") == "button" and e.text == "Save":
            e.click()
            time.sleep(1)
            return
        
    assert False, "Unable to locate the dialog's save button"             
    
# Local utility functions
def get_column(title):
    elts = world.firefox.find_elements_by_tag_name("h2")
    for e in elts:
        try:
            if e.text and e.text.strip().lower().find(title.lower()) > -1:
                return e.parent
        except StaleElementReferenceException:
            continue
    
    return None

def find_button_by_value(value, parent = None):
    
    if not parent:
        parent = world.firefox
    
    elts = parent.find_elements_by_css_selector("input[type=submit]")
    for e in elts:
        if e.get_attribute("value") == value:
            return e
    
    elts = parent.find_elements_by_css_selector("input[type=button]")
    for e in elts:
        if e.get_attribute("value") == value:
            return e
        
    elts = world.firefox.find_elements_by_tag_name("button")
    for e in elts:
        if e.get_attribute("type") == "button" and e.text == value:
            return e    
        
    # try the links too
    elts = parent.find_elements_by_tag_name("a")
    for e in elts:
        if e.text and e.text.strip() == value:
            return e
        
    return None

world.find_button_by_value = find_button_by_value
