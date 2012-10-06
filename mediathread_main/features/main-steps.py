from lettuce.django import django_url
from lettuce import before, after, world, step
import sys, time
from selenium.webdriver import ActionChains
from selenium.webdriver.support.select import Select

@step(u'video upload is enabled')
def video_upload_is_enabled(step):
    if world.using_selenium:
        world.firefox.get(django_url("/dashboard/addsource/"))
        try:
            elt = world.firefox.find_element_by_id("mediathread-video-upload")
            if elt: 
                elt.click()
                alert = world.firefox.switch_to_alert()
                alert.accept()
        except:
            pass # It's already enabled. That's ok.
        
        
@step(u'Given the selection visibility is set to "([^"]*)"')
def given_the_selection_visibility_is_value(step, value):
    if world.using_selenium:
        world.firefox.get(django_url("/dashboard/settings/"))
        
        if value == "Yes":
            elt = world.firefox.find_element_by_id("selection_visibility_yes")
            elt.click();
            int_value = 1
        else:
            elt = world.firefox.find_element_by_id("selection_visibility_no")
            elt.click();
            int_value = 0
        
        elt = world.firefox.find_element_by_id("selection_visibility_submit")
        if elt: 
            elt.click()
            alert = world.firefox.switch_to_alert()
            alert.accept()
            
            world.firefox.get(django_url("/"))
        

@step(u'I see ([0-9][0-9]?) sources?')
def i_see_count_source(step, count):
    if world.using_selenium:
        elts = world.firefox.find_elements_by_css_selector("div.archive")
        assert len(elts) == int(count), "Expected %s. Actually found %s" % (count, len(elts))

@step(u'I add YouTube to the class')
def when_i_add_youtube_to_the_class(step):
    if world.using_selenium:
        elt = world.firefox.find_element_by_id("you-tube")
        elt.click()
    
@step(u'I allow ([^"]*)s to upload videos')
def i_allow_level_to_upload_videos(step, level):    
    elt = world.firefox.find_element_by_name('upload_permission')
    assert elt != None, "Select element not found %s" % 'upload_permission'
    
    select = Select(elt)
    select.select_by_visible_text(level)
    
    form = world.firefox.find_element_by_name("form-upload-permission")
    form.submit()
    
@step(u'The selection visibility is "([^"]*)"')
def the_selection_visibility_is_value(step, value):
    if value == 'Yes':
        elt = world.firefox.find_element_by_id('selection_visibility_yes')
    else:
        elt = world.firefox.find_element_by_id('selection_visibility_no')
    
    assert elt.get_attribute('checked'), "The checked attribute was %s" % elt.get_attribute("checked")
    
@step(u'I can upload on behalf of other users')
def i_can_upload_on_behalf_of_other_users(step):
    elt = world.firefox.find_element_by_id('video_owners')

@step(u'I cannot upload on behalf of other users')
def i_cannot_upload_on_behalf_of_other_users(step):
    try:
        elt = world.firefox.find_element_by_id('video_owners')
        assert False, "This user can upload on behalf of other users"
    except:
        pass # expected
        

 