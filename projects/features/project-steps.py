from lettuce.django import django_url
from lettuce import before, after, world, step
import sys, time
from selenium.webdriver import ActionChains
from selenium.webdriver.support.select import Select
from mediathread.projects.models import Project

@step(u'There are no projects')
def there_are_no_projects(step):
    assert len(Project.objects.all()) == 0

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
    
@step(u'there is not an? ([^"]*) ([^"]*) panel')
def there_is_not_a_state_name_panel(step, state, name):
    """
    Keyword arguments:
    state -- open, closed
    name -- composition, assignment, discussion, collection 

    """
    try:
        panel = world.firefox.find_element_by_css_selector("td.panel-container.%s.%s" % (state.lower(), name.lower()))
        assert False, "Found panel named %s" % panel
    except:
        pass # expected
    
@step(u'the ([^"]*) panel has an? ([^"]*) button')
def the_panel_has_a_name_button(step, panel, name):
    panel = world.firefox.find_element_by_css_selector("td.panel-container.open.%s" % panel.lower())
    assert panel != None, "Can't find panel named %s" % panel
    
    btn = world.find_button_by_value(name, panel)
    assert btn != None, "Can't find button named %s" % name
    
@step(u'the ([^"]*) panel does not have an? ([^"]*) button')
def the_panel_does_not_have_a_name_button(step, panel, name):
    panel = world.firefox.find_element_by_css_selector("td.panel-container.open.%s" % panel.lower())
    assert panel != None, "Can't find panel named %s" % panel
    
    try:
        btn = world.find_button_by_value(name, panel)
        assert False, "Found a button named %s" % name
    except:
        pass # expected
    
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
    
@step(u'I see a ([^"]*) dialog')
def i_see_a_name_dialog(step, name):
    elt = world.firefox.find_element_by_css_selector('span.ui-dialog-title')
    assert elt != None and elt.text == name
    
@step(u'the project visibility is "([^"]*)"')
def the_project_visibility_is_level(step, level):
    elt = world.firefox.find_element_by_css_selector("input[name=publish]:checked")
    assert elt != None
    
    label_selector = "label[for=%s]" % elt.get_attribute("id")
    label = world.firefox.find_element_by_css_selector(label_selector)
    if label.text.strip() == level:
        return

    assert False, "The %s option is not checked" % (level)
    
@step(u'There is a project visibility "([^"]*)"')
def there_is_a_project_visibility_level(step, level):
    elts = world.firefox.find_elements_by_name("publish")
    assert len(elts) > 0
    
    for e in elts:
        label_selector = "label[for=%s]" % e.get_attribute("id")
        label = world.firefox.find_element_by_css_selector(label_selector)
        if label.text.strip() == level:
            return

    assert False, "No %s option found" % (level)
    
@step(u'There is not a project visibility "([^"]*)"')
def there_is_not_a_project_visibility_level(step, level):
    elts = world.firefox.find_elements_by_name("publish")
    assert len(elts) > 0
    
    for e in elts:
        label_selector = "label[for=%s]" % e.get_attribute("id")
        label = world.firefox.find_element_by_css_selector(label_selector)
        if label.text.strip() == level:
            assert False, "Found %s option" % (level)    
    
@step(u'Then I set the project visibility to "([^"]*)"')
def i_set_the_project_visibility_to_level(step, level):
    elts = world.firefox.find_elements_by_name("publish")
    assert len(elts) > 0
    
    for e in elts:
        label_selector = "label[for=%s]" % e.get_attribute("id")
        label = world.firefox.find_element_by_css_selector(label_selector)
        if label.text.strip() == level:
            e.click()
            return

    assert False, "No %s option found" % (level)
    
@step(u'I select ([^"]*)\'s response')
def i_select_username_s_response(step, username):
    elt = world.firefox.find_element_by_name("responses")
    
    select = Select(elt)
    for o in select.options:
        if o.text.find(username) > -1:
            select.select_by_visible_text(o.text)
            return
    assert False, "Unable to find a response for %s" % username

  
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
    n = 0
    for e in elts:
        a = e.find_element_by_css_selector("a.asset_title")
        if a.text == title:
            n += 1
    assert n == int(count), "There are %s projects named %s. Expected %s"  % (n, title, count)
     
    
@step(u'i save the changes')
def i_save_the_changes(step):
    elts = world.firefox.find_elements_by_tag_name("button")
    for e in elts:
        if e.get_attribute("type") == "button" and e.text == "Save":
            e.click()
            time.sleep(1)
            return
        
    assert False, "Unable to locate the dialog's save button"
    
@step(u'there is an? ([^"]*) "([^"]*)" project by ([^"]*)')
def there_is_a_status_title_project_by_author(step, status, title, author):
    elts = world.firefox.find_elements_by_css_selector("li.projectlist")
    if len(elts) < 1:
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
    
    
@step(u'there is a comment that begins "([^"]*)"')
def there_is_a_comment_that_begins_text(step, text):
    elts = world.firefox.find_elements_by_css_selector("div.threaded_comment_text")
    assert len(elts) > 0, "Expected to find at least one div.threaded_comment_text. Found 0"
    
    for e in elts:
        if e.text.startswith(text):
            return
    
    assert False, "Could not find a comment that begins with %s" % text
    