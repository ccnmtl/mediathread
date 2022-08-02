import time
from lettuce import world, step
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.expected_conditions import \
    invisibility_of_element_located, visibility_of_element_located
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.select import Select
import selenium.webdriver.support.ui as ui
from selenium.webdriver.common.keys import Keys


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
    except NoSuchElementException:
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
    except NoSuchElementException:
        assert False, msg


@step(u'the ([^"]*) panel has an? ([^"]*) button')
def the_panel_has_a_name_button(step, panel, name):
    selector = "td.panel-container.open.%s" % panel.lower()
    panel = world.browser.find_element_by_css_selector(selector)
    assert panel is not None, "Can't find panel named %s" % panel

    btn = world.find_button_by_value(name, panel)
    if btn is None:
        assert False, "Can't find button named %s" % name
    if btn.is_displayed() is False:
        assert False, "Button is not visible %s" % name


@step(u'the ([^"]*) panel does not have an? ([^"]*) button')
def the_panel_does_not_have_a_name_button(step, panel, name):
    selector = "td.panel-container.open.%s" % panel.lower()
    panel = world.browser.find_element_by_css_selector(selector)
    assert panel is not None, "Can't find panel named %s" % panel

    try:
        elt = world.find_button_by_value(name, panel)
        if elt is not None and elt.is_displayed():
            assert False, "Found a visible button named %s. [%s]" % \
                (name, elt.get_attribute('value'))
    except NoSuchElementException:
        pass  # expected


@step(u'the ([^"]*) panel does not have an author edit area')
def the_panel_does_not_have_an_author_edit_area(step, panel):
    selector = "td.panel-container.open.%s" % panel.lower()
    panel = world.browser.find_element_by_css_selector(selector)
    assert panel is not None, "Can't find panel named %s" % panel

    try:
        elt = panel.find_element_by_css_selector('.participant_list')
        if elt is not None and elt.is_displayed():
            assert False, "Found a visible author edit area"
    except NoSuchElementException:
        pass  # expected


@step(u'the ([^"]*) panel has an author edit area')
def the_panel_has_an_author_edit_area(step, panel):
    selector = "td.panel-container.open.%s" % panel.lower()
    panel = world.browser.find_element_by_css_selector(selector)
    assert panel is not None, "Can't find panel named %s" % panel

    elt = panel.find_element_by_css_selector('.participant_list')
    if elt is None:
        assert False, "Can't find an author edit area"
    if not elt.is_displayed():
        assert False, "Can't find an author edit area"


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
    q = '//ul/li/label[contains(text(),"{}")]'.format(level)
    wait = ui.WebDriverWait(world.browser, 5)
    wait.until(visibility_of_element_located((By.XPATH, q)))


@step(u'There is not a project visibility "([^"]*)"')
def there_is_not_a_project_visibility_level(step, level):
    elts = world.browser.find_elements_by_name("publish")
    assert len(elts) > 0

    for e in elts:
        label_selector = "label[for=%s]" % e.get_attribute("id")
        label = world.browser.find_element_by_css_selector(label_selector)
        if label.text.strip() == level:
            assert False, "Found %s option" % (level)


@step(u'I select ([^"]*)\'s response')
def i_select_username_s_response(step, username):
    elt = world.browser.find_element_by_name("responses")

    select = Select(elt)
    for o in select.options:
        if o.text.find(username) > -1:
            select.select_by_visible_text(o.text)
            return
    assert False, "Unable to find a response for %s" % username


@step(u'there is a comment from "([^"]*)"')
def there_is_a_comment_from_username(step, username):
    selector = "span.threaded_comment_author"
    elts = world.browser.find_elements_by_css_selector(selector)
    for e in elts:
        if e.text == username:
            return

    assert False, 'Cannot find comment from %s' % username


@step(u'Then I remember the "([^"]*)" link')
def then_i_remember_the_title_link(step, title):
    link = world.browser.find_element_by_partial_link_text(title)
    world.memory[title] = link.get_attribute('href')


@step(u'I navigate to the "([^"]*)" link')
def i_navigate_to_the_title_link(step, title):
    link = world.memory[title]
    world.browser.get(link)
    del (world.memory[title])


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
    except NoSuchElementException:
        try:
            selector = 'div.annotation-title'
            a = media_window.find_element_by_css_selector(selector)
            assert a.text == title
        except NoSuchElementException:
            msg = "Didn't find %s in the %s media window" % (title, panelname)
            assert False, msg


@step(u'I toggle the ([^"]*) panel')
def i_toggle_the_panelname_panel(step, panelname):
    selector = "div.pantab.%s" % panelname.lower()
    pantab = world.browser.find_element_by_css_selector(selector)
    assert pantab, "Cannot find the %s pantab" % panelname

    pantab.click()


@step(u'I click edit item for "([^"]*)"')
def when_i_click_edit_item_for_title(step, title):
    selector = ".gallery-item-project"
    items = world.browser.find_elements_by_css_selector(selector)
    for item in items:
        try:
            item.find_element_by_partial_link_text(title)
            elt = item.find_element_by_css_selector(".edit_icon")
            elt.click()
            return
        except NoSuchElementException:
            continue

    assert False, "Unable to find the %s item" % title


@step(u'I click create selection for "([^"]*)"')
def i_click_create_selection_for_title(step, title):
    selector = ".gallery-item-project"
    items = world.browser.find_elements_by_css_selector(selector)
    for item in items:
        try:
            item.find_element_by_partial_link_text(title)
            elt = item.find_element_by_css_selector(".create_annotation_icon")
            assert elt, "Unable to find the + link for item" % title
            elt.click()
            return
        except NoSuchElementException:
            continue

    assert False, "Unable to find the %s item" % title


@step(u'I click edit selection for "([^"]*)"')
def i_click_edit_selection_for_title(step, title):
    selector = ".selection-level-info"
    items = world.browser.find_elements_by_css_selector(selector)
    for item in items:
        try:
            item.find_element_by_partial_link_text(title)
            elt = item.find_element_by_css_selector(".edit-selection-icon")
            elt.click()
            return
        except NoSuchElementException:
            continue

    assert False, "Unable to find the %s selection" % title


@step(u'the "([^"]*)" form appears')
def the_title_form_appears(step, title):
    try:
        fid = None
        if title == 'Create Selection' or title == 'Edit Selection':
            fid = 'annotation-current'
        elif title == 'Edit Item':
            fid = 'asset-global-annotation-quick-edit'

        wait = ui.WebDriverWait(world.browser, 5)
        wait.until(visibility_of_element_located((By.ID, fid)))
    except TimeoutException:
        assert False, '%s form did not appear' % title


@step(u'the "([^"]*)" form disappears')
def the_title_form_disappears(step, title):
    try:
        fid = None
        if title == 'Create Selection' or title == 'Edit Selection':
            fid = 'annotation-current'
        elif title == 'Edit Item':
            fid = 'asset-global-annotation-quick-edit'

        wait = ui.WebDriverWait(world.browser, 5)
        wait.until(invisibility_of_element_located((By.ID, fid)))

        q = 'div.ajaxloader'
        wait = ui.WebDriverWait(world.browser, 5)
        wait.until(invisibility_of_element_located((By.CSS_SELECTOR, q)))
    except TimeoutException:
        assert False, '%s form did not appear' % title


@step(u'I set the selection tags field to "([^"]*)"')
def i_set_the_selection_tags_field_to_value(step, value):
    q = '#edit-annotation-form #s2id_id_annotation-tags .select2-input'
    wait = ui.WebDriverWait(world.browser, 5)
    wait.until(visibility_of_element_located((By.CSS_SELECTOR, q)))
    elt = world.browser.find_element_by_css_selector(q)
    elt.send_keys(value)
    elt.send_keys(Keys.TAB)
    time.sleep(1)


@step(u'I set the item tags field to "([^"]*)"')
def i_set_the_item_tags_field_to_value(step, value):
    q = '#edit-global-annotation-form #s2id_id_annotation-tags .select2-input'
    wait = ui.WebDriverWait(world.browser, 5)
    wait.until(visibility_of_element_located((By.CSS_SELECTOR, q)))
    elt = world.browser.find_element_by_css_selector(q)
    elt.send_keys(value)
    elt.send_keys(Keys.TAB)
    time.sleep(1)


@step(u'I click a gallery item')
def i_click_a_gallery_item(step):
    q = '.gallery-item'
    elt = world.browser.find_element_by_css_selector(q)
    ActionChains(world.browser).move_to_element(elt).perform()

    q = '.gallery-item-overlay'
    elt = world.browser.find_element_by_css_selector(q)
    elt.click()


@step(u'I call the selection assignment "([^"]*)"')
def i_call_the_selection_assignment_value(step, title):
    elt = world.browser.find_element_by_name('title')
    elt.clear()
    elt.send_keys(title)


@step(u'I write instructions for the selection assignment')
def i_write_instructions_for_the_selection_assignment(step):
    world.browser.execute_script(
        "tinyMCE.activeEditor.setContent('some instructions')")


@step(u'I set selection assignment visibility to "([^"]*)"')
def i_set_selection_assignment_visibility_to_value(step, value):
    q = "//input[@value='{}']".format(value)
    wait = ui.WebDriverWait(world.browser, 5)
    elt = wait.until(visibility_of_element_located((By.XPATH, q)))
    elt.click()


@step(u'I set selection assignment due date')
def i_set_selection_assignment_due_date(step):
    elt = world.browser.find_element_by_name('due_date')
    elt.send_keys('01/01/2030')


@step(u'I publish the selection assignment as "([^"]*)"')
def i_publish_the_selection_assignment_as_value(step, value):
    if value == 'Whole Class':
        q = "//input[@value='CourseProtected']"
    else:
        q = "//input[@value='PrivateEditorsAreOwners']"

    elt = world.browser.find_element_by_xpath(q)
    elt.click()


@step(u'I submit the selection assignment')
def i_submit_the_selection_assignment(step):
    wait = ui.WebDriverWait(world.browser, 5)
    elt = wait.until(visibility_of_element_located((By.ID, 'submit-project')))

    btn = elt.parent.find_element_by_css_selector('button.submit-response')
    btn.click()

    wait = ui.WebDriverWait(world.browser, 5)
    wait.until(invisibility_of_element_located((By.ID,
                                                'submit-project')))


@step(u'The feedback count is ([0-9])')
def the_feedback_count_is_value(step, value):
    q = 'span.feedback-count'
    elt = world.browser.find_element_by_css_selector(q)
    assert elt.text == value


@step(u'I add some feedback to the selection assignment response')
def i_add_some_feedback_to_the_selection_assignment_response(step):
    q = "//textarea[@name='comment']"
    elt = world.browser.find_element_by_xpath(q)
    elt.send_keys('good job')
