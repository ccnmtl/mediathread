from lettuce import world, step
from mediathread.projects.models import Project
from selenium.webdriver.support.select import Select
from urlparse import urlparse
import time


@step(u'There are no projects')
def there_are_no_projects(step):
    Project.objects.all().delete()

    n = Project.objects.count()
    assert n == 0, "Found %s projects. Expected 0" % n


@step(u'there is not an? ([^"]*) ([^"]*) panel')
def there_is_not_a_state_name_panel(step, state, name):
    """
    Keyword arguments:
    state -- open, closed
    name -- composition, assignment, discussion, collection

    """
    try:
        selector = "td.panel-container.%s.%s" % (state.lower(), name.lower())
        panel = world.browser.find_element_by_css_selector(selector)
        assert False, "Found panel named %s" % panel
    except:
        pass  # expected


@step(u'the ([^"]*) panel has an? ([^"]*) subpanel')
def the_name_panel_has_a_state_subpanel(step, name, state):
    selector = "td.panel-container.open.%s" % name.lower()
    panel = world.browser.find_element_by_css_selector(selector)
    assert panel is not None, "Can't find panel named %s" % panel

    selector = "td.panel-container.%s" % state
    msg = "Can't find %s subpanel in %s panel" % (state, name)

    try:
        subpanel = panel.find_element_by_css_selector(selector)
        assert subpanel is not None, msg
    except:
        assert False, msg


@step(u'the ([^"]*) panel has an? ([^"]*) button')
def the_panel_has_a_name_button(step, panel, name):
    selector = "td.panel-container.open.%s" % panel.lower()
    panel = world.browser.find_element_by_css_selector(selector)
    assert panel is not None, "Can't find panel named %s" % panel

    btn = world.find_button_by_value(name, panel)
    assert btn is not None, "Can't find button named %s" % name


@step(u'the ([^"]*) panel does not have an? ([^"]*) button')
def the_panel_does_not_have_a_name_button(step, panel, name):
    selector = "td.panel-container.open.%s" % panel.lower()
    panel = world.browser.find_element_by_css_selector(selector)
    assert panel is not None, "Can't find panel named %s" % panel

    try:
        world.find_button_by_value(name, panel)
        assert False, "Found a button named %s" % name
    except:
        pass  # expected


@step(u'I see a ([^"]*) dialog')
def i_see_a_name_dialog(step, name):
    elt = world.browser.find_element_by_css_selector('span.ui-dialog-title')
    assert elt is not None and elt.text == name


@step(u'the project visibility is "([^"]*)"')
def the_project_visibility_is_level(step, level):
    selector = "input[name=publish]:checked"
    elt = world.browser.find_element_by_css_selector(selector)
    assert elt is not None

    label_selector = "label[for=%s]" % elt.get_attribute("id")
    label = world.browser.find_element_by_css_selector(label_selector)
    if label.text.strip() == level:
        return

    assert False, "The %s option is not checked" % (level)


@step(u'There is a project visibility "([^"]*)"')
def there_is_a_project_visibility_level(step, level):
    elts = world.browser.find_elements_by_name("publish")
    assert len(elts) > 0

    for e in elts:
        label_selector = "label[for=%s]" % e.get_attribute("id")
        label = world.browser.find_element_by_css_selector(label_selector)
        if label.text.strip() == level:
            return

    assert False, "No %s option found" % (level)


@step(u'There is not a project visibility "([^"]*)"')
def there_is_not_a_project_visibility_level(step, level):
    elts = world.browser.find_elements_by_name("publish")
    assert len(elts) > 0

    for e in elts:
        label_selector = "label[for=%s]" % e.get_attribute("id")
        label = world.browser.find_element_by_css_selector(label_selector)
        if label.text.strip() == level:
            assert False, "Found %s option" % (level)


@step(u'Then I set the project visibility to "([^"]*)"')
def i_set_the_project_visibility_to_level(step, level):
    elts = world.browser.find_elements_by_name("publish")
    assert len(elts) > 0

    for e in elts:
        label_selector = "label[for=%s]" % e.get_attribute("id")
        label = world.browser.find_element_by_css_selector(label_selector)
        if label.text.strip() == level:
            e.click()
            return

    assert False, "No %s option found" % (level)


@step(u'I select ([^"]*)\'s response')
def i_select_username_s_response(step, username):
    elt = world.browser.find_element_by_name("responses")

    select = Select(elt)
    for o in select.options:
        if o.text.find(username) > -1:
            select.select_by_visible_text(o.text)
            return
    assert False, "Unable to find a response for %s" % username


@step(u'there is a comment that begins "([^"]*)"')
def there_is_a_comment_that_begins_text(step, text):
    selector = "div.threaded_comment_text"
    elts = world.browser.find_elements_by_css_selector(selector)
    assert len(elts) > 0, "Expected >= 1 div.threaded_comment_text. Found 0"

    for e in elts:
        if e.text.startswith(text):
            return

    time.sleep(1)

    selector = "div.threaded_comment_text"
    elts = world.browser.find_elements_by_css_selector(selector)
    for e in elts:
        if e.text.startswith(text):
            return

    assert False, "Could not find a comment that begins with %s" % text


@step(u'I insert "([^"]*)" into the text')
def i_insert_title_into_the_text(step, title):
    link = world.browser.find_element_by_partial_link_text(title)
    href = link.get_attribute("href")

    # strip the http://localhost:port off this href
    pieces = urlparse(href)

    insert_icon = world.browser.find_element_by_name(pieces.path)
    insert_icon.click()


@step(u'Then I remember the "([^"]*)" link')
def then_i_remember_the_title_link(step, title):
    link = world.browser.find_element_by_partial_link_text(title)
    world.memory[title] = link.get_attribute('href')


@step(u'I navigate to the "([^"]*)" link')
def i_navigate_to_the_title_link(step, title):
    link = world.memory[title]
    world.browser.get(link)
    del(world.memory[title])


@step(u'I click the "([^"]*)" citation in the ([^"]*) panel')
def i_click_the_link_citation_in_the_panelname_panel(step, link, panelname):
    selector = "td.panel-container.open.%s" % panelname.lower()
    panel = world.browser.find_element_by_css_selector(selector)
    assert panel is not None, "Can't find panel named %s" % panel

    # Click the link in the tinymc window
    anchors = panel.find_elements_by_css_selector("a.materialCitation")
    for a in anchors:
        if a.text == link:
            a.click()


@step(u'the ([^"]*) panel media window displays "([^"]*)"')
def the_panelname_panel_media_window_displays_title(step, panelname, title):
    selector = "td.panel-container.open.%s" % panelname.lower()
    panel = world.browser.find_element_by_css_selector(selector)
    assert panel, "Cannot find the %s panel" % panelname

    selector = 'div.asset-view-published'
    media_window = panel.find_element_by_css_selector(selector)
    try:
        a = media_window.find_element_by_css_selector('div.annotation-title a')
        assert a.text == title
    except:
        try:
            selector = 'div.annotation-title'
            a = media_window.find_element_by_css_selector(selector)
            assert a.text == title
        except:
            msg = "Didn't find %s in the %s media window" % (title, panelname)
            assert False, msg


@step(u'I toggle the ([^"]*) panel')
def i_toggle_the_panelname_panel(step, panelname):
    selector = "div.pantab.%s" % panelname.lower()
    pantab = world.browser.find_element_by_css_selector(selector)
    assert pantab, "Cannot find the %s pantab" % panelname

    pantab.click()
