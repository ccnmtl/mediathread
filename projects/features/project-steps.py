from lettuce.django import django_url
from lettuce import before, after, world, step
import sys, time
from selenium.webdriver import ActionChains
from selenium.webdriver.support.select import Select

@step(u'There is an? ([^"]*) panel')
def there_is_a_name_panel(step, name):
    elts = world.firefox.find_elements_by_css_selector("td.panhandle-stripe div.label")
    if len(elts) < 1:
        time.sleep(1)
        elts = world.firefox.find_elements_by_css_selector("td.panhandle-stripe div.label")
        
    assert len(elts) > 0, "Expected at least 1 td.panhandle-stripe div.label but found %s" % len(elts)
    for e in elts:
        if e.text.strip().lower() == name.lower():
            return
        
    assert False, 'No panel named %s found.' % name
    
@step(u'the ([^"]*) panel has a ([^"]*) button')
def the_panel_has_a_name_button(step, panel, name):
    panel = world.firefox.find_element_by_css_selector("td.panel-container.open.%s" % panel.lower())
    assert panel != None, "Can't find panel named %s" % panel
    
    btn = world.find_button_by_value(name, panel)
    assert btn != None, "Can't find button named %s" % name
    
@step(u'I call the ([^"]*) "([^"]*)"')
def i_call_the_composition_title(step, panel, title):
    panel = world.firefox.find_element_by_css_selector("td.panel-container.open.%s" % panel.lower())
    assert panel != None, "Can't find panel named %s" % panel
    
    input = panel.find_element_by_name("title")
    input.clear()
    input.send_keys(title)
    
@step(u'I write some text for the ([^"]*)')
def i_write_some_text_for_the_composition(step, panel):
    panel = world.firefox.find_element_by_css_selector("td.panel-container.open.%s" % panel.lower())
    assert panel != None, "Can't find panel named %s" % panel
    
    frame = panel.find_element_by_tag_name("iframe")
    world.firefox.switch_to_frame(frame)
    input = world.firefox.find_element_by_class_name("mceContentBody")
    input.send_keys("""The Columbia Center for New Teaching and Learning was (CCNMTL)
                    was founded at Columbia University in 1999 to enhance teaching and
                    learning through the purposeful use of new media and technology""")
    
    world.firefox.switch_to_default_content()

    
