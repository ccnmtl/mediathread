# -*- coding: utf-8 -*-
import re
import time
from urlparse import urlparse

from django.conf import settings
from django.core import management
from django.core.urlresolvers import reverse
from django.test import client
from lettuce import before, after, world, step
from lettuce import django
from selenium.common.exceptions import NoSuchElementException, \
    StaleElementReferenceException, InvalidElementStateException
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.expected_conditions import (
    visibility_of_element_located, invisibility_of_element_located,
    visibility_of)
from selenium.webdriver.support.ui import WebDriverWait

from mediathread.assetmgr.models import Asset
from mediathread.factories import MediathreadTestMixin
from mediathread.projects.models import Project
import selenium.webdriver.support.ui as ui


try:
    from lxml import html
    from selenium import webdriver
    from selenium.webdriver.firefox.firefox_profile import FirefoxProfile
except:
    pass


@before.harvest
def migrate_database(variables):
    management.call_command('migrate', verbosity=0, interactive=False)


@before.each_scenario
def reset_database(variables):
    world.using_selenium = False
    management.call_command('flush', verbosity=0, interactive=False)

    world.browser.get(django.django_url("/test/clear/"))

    # add the sample course and some user data by default
    world.mixin = MediathreadTestMixin()
    world.mixin.setup_sample_course()


@before.all
def setup_browser():
    world.browser = None
    browser = getattr(settings, 'BROWSER', "Headless")
    if browser == 'Firefox':
        ff_profile = FirefoxProfile()
        ff_profile.set_preference("webdriver_enable_native_events", False)
        world.browser = webdriver.Firefox(ff_profile)
    elif browser == 'Chrome':
        world.browser = webdriver.Chrome()
    elif browser == "Headless":
        world.browser = webdriver.PhantomJS(
            desired_capabilities={'handlesAlerts': True})

    world.client = client.Client()
    world.using_selenium = False

    world.browser.set_window_position(0, 0)
    world.browser.set_window_size(1024, 768)

    # Wait implicitly for 2 seconds
    world.browser.implicitly_wait(2)

    # stash
    world.memory = {}


@after.all
def teardown_browser(total):
    world.browser.quit()


@step(u'Using selenium')
def using_selenium(step):
    world.using_selenium = True


@step(u'Finished using selenium')
def finished_selenium(step):
    world.using_selenium = False


# Data Loading Functionality
@step(u'there is an alternate course')
def there_is_an_alternate_course(step):
    world.mixin.setup_alternate_course()


@step(u'there is a sample assignment')
def there_is_a_sample_assignment(step):
    world.mixin.setup_sample_assignment()


@step(u'there is a sample response')
def there_is_a_sample_response(step):
    world.mixin.setup_sample_assignment_and_response()


@step(u'there is a sample selection assignment')
def there_is_a_sample_selection_assignment(step):
    world.mixin.setup_sample_selection_assignment()


@step(u'there is a sample selection assignment and response')
def there_is_a_sample_selection_response(step):
    world.mixin.setup_sample_selection_assignment_and_response()


@step(u'there are sample assets')
def there_are_sample_assets(step):
    world.mixin.setup_sample_assets()


@step(u'there are sample suggested collections')
def there_are_sample_suggested_collections(step):
    world.mixin.setup_suggested_collection()


@step(u'there is a teaching assistant in Sample Course')
def there_is_a_teaching_assistant_in_sample_course(step):
    world.mixin.setup_teaching_assistant()


@step(r'I access the url "(.*)"')
def access_url(step, url):
    if world.using_selenium:
        world.browser.get(django.django_url(url))
    else:
        response = world.client.get(django.django_url(url))
        world.dom = html.fromstring(response.content)


@step(u'the ([^"]*) workspace is loaded')
def the_name_workspace_is_loaded(step, name):
    workspace_id = None
    if (name == "composition" or name == "assignment" or
            name == "home" or name == "collection" or name == 'taxonomy'):
        workspace_id = "loaded"
    elif name == "asset":
        workspace_id = "asset-loaded"
    else:
        assert False, "No selector configured for %s" % name

    wait = ui.WebDriverWait(world.browser, 5)
    wait.until(lambda driver: world.browser.find_element_by_id(workspace_id))


@step(u'my browser resolution is ([^"]*) x ([^"]*)')
def my_browser_resolution_is_width_x_height(step, width, height):
    world.browser.set_window_size(int(width), int(height))


@step(u'I am ([^"]*) in ([^"]*)')
def i_am_username_in_course(step, username, coursename):
    if world.using_selenium:
        world.browser.get(django.django_url("/accounts/logout/?next=/"))
        world.browser.get(django.django_url("accounts/login/?next=/"))

        wait = ui.WebDriverWait(world.browser, 5)
        wait.until(visibility_of_element_located((By.ID, 'guest-login')))

        elt = world.browser.find_element_by_id('guest-login')
        elt.click()

        username_field = world.browser.find_element_by_id("id_username")
        username_field.send_keys(username)

        password_field = world.browser.find_element_by_id("id_password")
        password_field.send_keys("test")

        form = world.browser.find_element_by_name("login_local")
        form.submit()

        if re.match(r'^instructor', username):
            course = world.browser.find_element_by_css_selector(
                'a.choose-course')
            course.click()

        wait = ui.WebDriverWait(world.browser, 5)
        wait.until(lambda driver: world.browser.title.find("Home") > -1)

        wait.until(lambda driver: world.browser.find_element_by_id("loaded"))

        course_title = world.browser.find_element_by_id("course_title_link")
        msg = ("Expected the %s class, but found the %s class" %
               (coursename, course_title.text))
        assert course_title.text.find(coursename) > -1, msg

        assert username in world.browser.page_source, world.browser.page_source
    else:
        world.client.login(username=username, password='test')


@step(u'I am not logged in')
def i_am_not_logged_in(step):
    if world.using_selenium:
        world.browser.get(django.django_url("/accounts/logout/?next=/"))
    else:
        world.client.logout()


@step(u'I log out')
def i_log_out(step):
    if world.using_selenium:
        world.browser.get(django.django_url("/accounts/logout/?next=/"))
    else:
        response = world.client.get(
            django.django_url("/accounts/logout/?next=/"), follow=True)
        world.response = response
        world.dom = html.fromstring(response.content)


@step(u'I am at the ([^"]*) page')
def i_am_at_the_name_page(step, name):
    if world.using_selenium:
        wait = ui.WebDriverWait(world.browser, 5)
        wait.until(lambda driver: world.browser.title.find(name) > -1)


@step(u'I type "([^"]*)" for ([^"]*)')
def i_type_value_for_field(step, value, field):
    if world.using_selenium:
        selector = "input[name=%s]" % field
        elt = world.browser.find_element_by_css_selector(selector)
        assert elt is not None, "Cannot locate input field named %s" % field
        elt.send_keys(value)


@step(u'I click the ([^"]*) button')
def i_click_the_value_button(step, value):
    if world.using_selenium:
        elt = find_button_by_value(value)
        if elt is None:
            assert False, "Cannot locate button named %s" % value

        wait = ui.WebDriverWait(world.browser, 5)
        wait.until(visibility_of(elt))
        elt.click()


@step(u'there is not an? "([^"]*)" link')
def there_is_not_a_text_link(step, text):
    if not world.using_selenium:
        for a in world.dom.cssselect("a"):
            if a.text:
                if text.strip().lower() in a.text.strip().lower():
                    href = a.attrib['href']
                    response = world.client.get(django.django_url(href))
                    world.dom = html.fromstring(response.content)
                    assert False, "found the '%s' link" % text
    else:
        wait = ui.WebDriverWait(world.browser, 5)
        wait.until(invisibility_of_element_located((By.PARTIAL_LINK_TEXT,
                                                    text)))


@step(u'there is an? "([^"]*)" link')
def there_is_a_text_link(step, text):
    if not world.using_selenium:
        for a in world.dom.cssselect("a"):
            if a.text:
                if text.strip().lower() in a.text.strip().lower():
                    href = a.attrib['href']
                    response = world.client.get(django.django_url(href))
                    world.dom = html.fromstring(response.content)
                    return
        assert False, "could not find the '%s' link" % text
    else:
        wait = ui.WebDriverWait(world.browser, 5)
        wait.until(visibility_of_element_located((By.PARTIAL_LINK_TEXT, text)))


@step(u'I click the "([^"]*)" link')
def i_click_the_link(step, text):
    if not world.using_selenium:
        for a in world.dom.cssselect("a"):
            if a.text:
                if text.strip().lower() in a.text.strip().lower():
                    href = a.attrib['href']
                    response = world.client.get(django.django_url(href))
                    world.dom = html.fromstring(response.content)
                    return
        assert False, "could not find the '%s' link" % text
    else:
        try:
            link = world.browser.find_element_by_partial_link_text(text)
            assert link.is_displayed()
            link.click()
        except NoSuchElementException:
            world.browser.get_screenshot_as_file("/tmp/selenium.png")
            assert False, text


@step(u'I scroll to the "([^"]*)" link')
def i_scroll_to_the_link(step, text):
    try:
        link = world.browser.find_element_by_partial_link_text(text)
        script = "return arguments[0].scrollIntoView();"
        world.browser.execute_script(script, link)
        assert link.is_displayed()
    except NoSuchElementException:
        world.browser.get_screenshot_as_file("/tmp/selenium.png")
        assert False, link.location


@step(u'I am in the ([^"]*) class')
def i_am_in_the_coursename_class(step, coursename):
    if world.using_selenium:
        course_title = world.browser.find_element_by_id("course_title_link")
        msg = ("Expected the %s class, but found the %s class" %
               (coursename, course_title.text))
        assert course_title.text.find(coursename) > -1, msg


@step(u'there is an? ([^"]*) button')
def there_is_a_value_button(step, value):
    elt = find_button_by_value(value)
    assert elt, "Cannot locate button named %s" % value


@step(u'there is not an? ([^"]*) button')
def there_is_not_a_value_button(step, value):
    elt = find_button_by_value(value)
    assert elt is None, "Found button named %s" % value


@step(u'I wait (\d+) seconds?')
def i_wait_count_seconds(step, count):
    n = int(count)
    time.sleep(n)


@step(u'I see "([^"]*)"')
def i_see_text(step, text):
    try:
        assert text in world.browser.page_source
    except AssertionError:
        time.sleep(1)
        assert text in world.browser.page_source, world.browser.page_source


@step(u'I do not see "([^"]*)"')
def i_do_not_see_text(step, text):
    assert text not in world.browser.page_source, world.browser.page_source


@step(u'I cancel the action')
def i_cancel_the_action(step):
    dialog = world.browser.find_element_by_id("dialog-confirm").parent
    btns = dialog.find_elements_by_tag_name("button")
    for btn in btns:
        try:
            span = btn.find_element_by_css_selector("span.ui-button-text")
        except NoSuchElementException:
            continue
        if span.text == "Cancel":
            btn.click()
            time.sleep(2)
            return

    world.browser.get_screenshot_as_file("/tmp/selenium.png")
    assert False, "Unable to locate the dialog's Cancel button"


@step(u'I confirm the action')
def i_confirm_the_action(step):
    wait = ui.WebDriverWait(world.browser, 5)
    wait.until(visibility_of_element_located((By.ID, 'dialog-confirm')))

    dialog = world.browser.find_element_by_id("dialog-confirm").parent
    btns = dialog.find_elements_by_tag_name("button")
    for btn in btns:
        try:
            span = btn.find_element_by_css_selector("span.ui-button-text")
        except NoSuchElementException:
            continue
        if span.text == "OK":
            btn.click()
            wait = ui.WebDriverWait(world.browser, 5)
            wait.until(invisibility_of_element_located((By.ID,
                                                        'dialog-confirm')))
            time.sleep(2)
            return

    assert False, "Unable to locate the dialog's OK button"


@step(u'I open the ([^"]*) menu')
def i_open_the_title_menu(step, title):
    selector = "div.settings_menu.%s" % title
    elt = world.browser.find_element_by_css_selector(selector)
    elt.click()


@step(u'there is no ([^"]*) menu')
def there_is_no_title_menu(step, title):
    try:
        selector = "div.settings_menu.%s" % title
        world.browser.find_element_by_css_selector(selector)
        assert False, "Found %s menu" % title
    except NoSuchElementException:
        pass  # expected


@step(u'there is an? ([^"]*) column')
def there_is_a_title_column(step, title):
    elts = world.browser.find_elements_by_tag_name("h2")

    for e in elts:
        if e.text and e.text.strip().lower().find(title.lower()) > -1:
            return

    assert False, "Unable to find a column entitled %s" % title


@step(u'there is not an? ([^"]*) column')
def there_is_not_a_title_column(step, title):
    elts = world.browser.find_elements_by_tag_name("h2")
    for e in elts:
        if e.text and e.text.strip().lower().startswith(title.lower()):
            assert False, "Found a column entitled %s" % title


@step(u'there is help for the ([^"]*) column')
def there_is_help_for_the_title_column(step, title):
    elts = world.browser.find_elements_by_tag_name("h2")
    for e in elts:
        if e.text and e.text.strip().lower().startswith(title.lower()):
            e.parent.find_element_by_css_selector(
                "div.actions input.help-tab-icon")
            return

    assert False, "No help found for %s" % title


@step(u'there is no help for the ([^"]*) column')
def there_is_no_help_for_the_title_column(step, title):
    elts = world.browser.find_elements_by_tag_name("h2")
    for e in elts:
        if e.text and e.text.strip().lower().startswith(title.lower()):
            try:
                e.parent.find_element_by_css_selector(
                    "div.actions input.help-tab-icon")
                assert False, "Help found for %s" % title
            except NoSuchElementException:
                return  # Expected outcome


@step(u'I\'m told "([^"]*)"')
def i_m_told_text(step, text):
    wait = ui.WebDriverWait(world.browser, 5)
    wait.until(visibility_of_element_located((By.ID, "dialog-confirm")))

    dlg = world.browser.find_element_by_id("dialog-confirm")
    assert dlg.text.startswith(text), "Alert text invalid: %s" % dlg.text


@step(u'I select "([^"]*)" as the owner')
def i_select_name_as_the_owner(step, name):
    selector = "div.switcher_collection_chooser"
    m = world.browser.find_element_by_css_selector(selector)
    assert m, 'Unable to find the owner menu'

    m.find_element_by_css_selector("a.switcher-top").click()

    owners = m.find_elements_by_css_selector("a.switcher-choice.owner")
    for o in owners:
        if o.text.find(name) > -1:
            o.click()
            time.sleep(2)
            return

    assert False, "Unable to find owner %s" % name


@step(u'I select "([^"]*)" as the owner in the ([^"]*) column')
def i_select_name_as_the_owner_in_the_title_column(step, name, title):
    column = get_column(title)

    m = column.find_element_by_css_selector("div.switcher_collection_chooser")

    assert m, 'Unable to find the owner menu'

    m.find_element_by_css_selector("a.switcher-top").click()

    owners = m.find_elements_by_css_selector("a.switcher-choice.owner")
    for o in owners:
        if o.text.find(name) > -1:
            o.click()
            return

    assert False, "Unable to find owner %s" % name


@step(u'the owner is "([^"]*)" in the ([^"]*) column')
def the_owner_is_name_in_the_title_column(step, name, title):
    selector = ("//h2[contains(.,'{}')]/../../../"
                "descendant::a[contains(@class,'switcher-top')]"
                "//span[@class='title'][contains(text(),'{}')]").format(title,
                                                                        name)

    wait = ui.WebDriverWait(world.browser, 5)
    wait.until(visibility_of_element_located((By.XPATH, selector)))


@step(u'the collection panel has a "([^"]*)" item')
def the_collection_panel_has_a_title_item(step, title):
    ''' Full collection in the asset worksapce '''
    selector = (
        "//tr[@class='asset-workspace-content-row']"
        "//div[contains(@class,'gallery-item')]"
        "//a[contains(@class,'asset-title-link')]"
        "[contains(text(),'{}')]").format(title)

    wait = ui.WebDriverWait(world.browser, 5)
    wait.until(visibility_of_element_located((By.XPATH, selector)))


@step(u'the collection panel has no "([^"]*)" item')
def the_collection_panel_has_no_title_item(step, title):
    ''' Full collection in the asset worksapce '''
    selector = (
        "//tr[@class='asset-workspace-content-row']"
        "//div[contains(@class,'gallery-item')]"
        "//a[contains(@class,'asset-title-link')]"
        "[contains(text(),'{}')]").format(title)
    elts = world.browser.find_elements_by_xpath(selector)
    assert len(elts) == 0


@step(u'I click the "([^"]*)" item ([^"]*) icon')
def i_click_the_title_item_name_icon(step, title, name):
    time.sleep(1)
    select = "div.gallery-item"
    items = world.browser.find_elements_by_css_selector(select)
    for item in items:
        try:
            item.find_element_by_partial_link_text(title)
        except NoSuchElementException:
            continue

        try:
            if name == "delete":
                icon = item.find_element_by_css_selector(".%s_icon" % name)
            elif name == "edit":
                s = "a.%s-asset-inplace" % name
                icon = item.find_element_by_css_selector(s)

            icon.click()
            return  # found the link & the icon
        except NoSuchElementException:
            assert False, "Item %s does not have a %s icon." % (title, name)

    assert False, "Unable to find the %s item" % title


@step(u'Given publish to world is ([^"]*)')
def given_publish_to_world_is_value(step, value):
    if world.using_selenium:
        world.browser.get(django.django_url("/dashboard/settings/"))

        if value == "enabled":
            elt = world.browser.find_element_by_id(
                "allow_public_compositions_yes")
            elt.click()
        else:
            elt = world.browser.find_element_by_id(
                "allow_public_compositions_no")
            elt.click()

        elt = world.browser.find_element_by_id(
            "allow_public_compositions_submit")

        if elt:
            elt.click()
            world.browser.get(django.django_url("/"))


@step(u'Then publish to world is ([^"]*)')
def then_publish_to_world_is_value(step, value):
    if value == 'enabled':
        elt = world.browser.find_element_by_id('allow_public_compositions_yes')
    else:
        elt = world.browser.find_element_by_id('allow_public_compositions_no')

    msg = "The checked attribute was %s" % elt.get_attribute("checked")
    assert elt.get_attribute('checked'), msg


@step(u'The "([^"]*)" project has no delete icon')
def the_title_project_has_no_delete_icon(step, title):
    time.sleep(1)
    link = world.browser.find_element_by_partial_link_text(title)
    try:
        link.parent.find_element_by_css_selector(".delete_icon")
        assert False, "%s does have a delete icon" % title
    except NoSuchElementException:
        assert True, "Item does not have a delete icon"


@step(u'The "([^"]*)" project has a delete icon')
def the_title_project_has_a_delete_icon(step, title):
    link = world.browser.find_element_by_partial_link_text(title)
    link.parent.find_element_by_css_selector(".delete_icon")


@step(u'I click the "([^"]*)" project delete icon')
def i_click_the_title_project_delete_icon(step, title):
    link = world.browser.find_element_by_partial_link_text(title)
    img = link.parent.find_element_by_css_selector(".delete_icon")
    img.click()


@step(u'the instructor panel has ([0-9][0-9]?) projects? named "([^"]*)"')
def the_instructor_panel_has_count_projects_named_title(step, count, title):
    elts = world.browser.find_elements_by_css_selector("ul.instructor-list li")
    n = 0
    for e in elts:
        a = e.find_element_by_css_selector("a")
        if a.text == title:
            n += 1

    msg = "Instructor panel had %s projects named %s. Expected %s" % (n,
                                                                      title,
                                                                      count)
    assert n == int(count), msg


@step(u'the composition panel has ([0-9][0-9]?) projects? named "([^"]*)"')
def the_composition_panel_has_count_projects_named_title(step, count, title):
    elts = world.browser.find_elements_by_css_selector("li.projectlist")

    n = 0
    for e in elts:
        a = e.find_element_by_css_selector("a.asset_title")
        if a.text == title:
            n += 1
    assert n == int(count), "%s projects named %s. Expected %s" % (n,
                                                                   title,
                                                                   count)


@step(u'the composition panel has ([0-9][0-9]?) responses? named "([^"]*)"')
def the_composition_panel_has_count_responses_named_title(step, count, title):
    elts = world.browser.find_elements_by_css_selector("li.projectlist")

    n = 0
    for e in elts:
        a = e.find_element_by_css_selector("a.metadata-value-response")
        if a.text == title:
            n += 1
    assert n == int(count), "%s responses named %s. Expected %s" % (n,
                                                                    title,
                                                                    count)


@step(u'there is an? ([^"]*) ([^"]*) panel')
def there_is_a_state_name_panel(step, state, name):
    """
    Keyword arguments:
    state -- open, closed
    name -- composition, assignment, discussion, collection
    """
    selector = "td.panel-container.%s.%s" % (state.lower(), name.lower())

    try:
        panel = world.browser.find_element_by_css_selector(selector)
    except NoSuchElementException:
        time.sleep(2)
        panel = world.browser.find_element_by_css_selector(selector)

    assert panel is not None, "Can't find panel named %s" % panel


@step(u'I call the ([^"]*) "([^"]*)"')
def i_call_the_panel_title(step, panel, title):
    selector = "td.panel-container.open.%s" % panel.lower()
    panel = world.browser.find_element_by_css_selector(selector)
    assert panel is not None, "Can't find panel named %s" % panel

    elt = panel.find_element_by_name("title")
    elt.clear()
    elt.send_keys(title)


@step(u'the ([^"]*) is called "([^"]*)"')
def the_panel_is_called_title(step, panel, title):
    selector = "td.panel-container.open.%s" % panel.lower()
    panel = world.browser.find_element_by_css_selector(selector)
    assert panel is not None, "Can't find panel named %s" % panel

    elt = panel.find_element_by_name("title")
    val = elt.get_attribute("value")
    assert val == title, "Nope: %s" % val


@step(u'I write some text for the ([^"]*)')
def i_write_some_text_for_the_panel(step, panel):
    if getattr(settings, 'BROWSER', None) != "Headless":
        selector = "td.panel-container.open.%s" % panel.lower()
        panel = world.browser.find_element_by_css_selector(selector)
        assert panel is not None, "Can't find panel named %s" % panel

        frame = panel.find_element_by_tag_name("iframe")
        world.browser.switch_to_frame(frame)
        elt = world.browser.find_element_by_class_name("mce-content-body")
        elt.send_keys(
            """The Columbia Center for New Teaching and Learning
            was (CCNMTL) was founded at Columbia University in 1999
            to enhance teaching and learning through the purposeful
            use of new media and technology""")

        world.browser.switch_to_default_content()


@step(u'the composition "([^"]*)" has text')
def the_composition_title_has_text(step, title):
    project = Project.objects.get(title=title)

    if len(project.body) < 1:
        project.body = """The Columbia Center for New Teaching and Learning
            was (CCNMTL) was founded at Columbia University in 1999
            to enhance teaching and learning through the purposeful
            use of new media and technology"""
        project.save()


@step(u'there is an? ([^"]*) "([^"]*)" reply by ([^"]*)')
def there_is_a_status_title_reply_by_author(step, status, title, author):
    selector = "div.assignment-listitem.response"
    elts = world.browser.find_elements_by_css_selector(selector)
    assert len(elts) > 0, "Expected at least 1 response. 0 found"

    for e in elts:
        title_elt = e.find_element_by_css_selector("a.metadata-value-response")
        title_parent = title_elt.parent

        if title_elt.text.strip().startswith(title):
            # author
            author_elt = title_parent.find_element_by_css_selector(
                "span.metadata-value-author")
            msg = ("%s author is [%s]. Expected [%s]." %
                   (title, author_elt.text.strip(), author))
            assert author_elt.text.strip() == author, msg

            # status
            status_elt = title_parent.find_element_by_css_selector(
                "span.metadata-value-status")
            msg = ("%s status starts with [%s]. Expected [%s]" %
                   (title, status_elt.text.strip().lower(), status))
            assert status_elt.text.strip().lower().startswith(status), msg

            return

    assert False, "Unable to find assignment response named %s" % title


@step(u'there is an? ([^"]*) "([^"]*)" project by ([^"]*)')
def there_is_a_status_title_project_by_author(step, status, title, author):
    elts = world.browser.find_elements_by_css_selector("li.projectlist")
    assert len(elts) > 0, "Expected at least 1 project. Found 0"

    assignment = False
    for e in elts:
        try:
            title_elt = e.find_element_by_css_selector(
                "a.asset_title.type-project")
        except NoSuchElementException:
            try:
                title_elt = e.find_element_by_css_selector(
                    "a.asset_title.type-assignment")
                assignment = True
            except NoSuchElementException:
                world.browser.get_screenshot_as_file("/tmp/selenium.png")
                assert False, "Cannot find the title %s css selector"

        if title_elt.text.strip().startswith(title):
            # type
            if assignment:
                type_elt = e.find_element_by_css_selector(
                    "span.metadata-value-assignment")
                assert (type_elt.text.strip() == "COMPOSITION ASSIGNMENT" or
                        type_elt.text.strip() == "SELECTION ASSIGNMENT")
            else:
                type_elt = e.find_element_by_css_selector(
                    "span.metadata-value-composition")
                assert type_elt.text.strip() == "COMPOSITION"

            if not assignment:
                # author
                author_elt = e.find_element_by_css_selector(
                    "span.metadata-value-author")
                msg = ("%s author is [%s]. Expected [%s]." %
                       (title, author_elt.text.strip(), author))
                assert author_elt.text.strip() == author, msg

                # status
                status_elt = e.find_element_by_css_selector(
                    "span.metadata-value-status")
                msg = ("%s status starts with [%s]. Expected [%s]" %
                       (title, status_elt.text.strip().lower(), status))
                assert status_elt.text.strip().lower().startswith(status), msg

                # make sure there is no response
                try:
                    selector = '.assignment-listitem.response'
                    elt = e.find_element_by_css_selector(selector)
                    assert elt is None, 'A project should not have a response'
                except NoSuchElementException:
                    pass  # expected

            return

    assert False, "Unable to find project named %s" % title


@step(u'I take a picture')
def i_take_a_picture(step):
    world.browser.get_screenshot_as_file("/tmp/selenium.png")


@step(u'The ([^"]*) title is "([^"]*)"')
def the_panel_title_is_value(step, panel, value):
    selector = "td.panel-container.open.%s" % panel.lower()
    panel = world.browser.find_element_by_css_selector(selector)
    assert panel is not None, "Can't find panel named %s" % panel

    h1 = panel.find_element_by_css_selector("h1.project-title")
    msg = "Expected %s title %s. Found %s" % (panel, value, h1.text.strip())
    assert h1.text.strip() == value, msg


@step(u'i save the changes')
def i_save_the_changes(step):
    elts = world.browser.find_elements_by_tag_name("button")
    for e in elts:
        if e.get_attribute("type") == "button" and e.text == "Save":
            e.click()
            time.sleep(2)
            return

    assert False, "Unable to locate the dialog's save button"


@step(u'Given the selection visibility is set to "([^"]*)"')
def given_the_selection_visibility_is_value(step, value):
    if world.using_selenium:
        world.browser.get(django.django_url("/dashboard/settings/"))

        if value == "Yes":
            elt = world.browser.find_element_by_id("selection_visibility_yes")
            elt.click()
        else:
            elt = world.browser.find_element_by_id("selection_visibility_no")
            elt.click()

        elt = world.browser.find_element_by_id("selection_visibility_submit")
        if elt:
            elt.click()
            world.browser.get(django.django_url("/"))


@step(u'Given the item visibility is set to "([^"]*)"')
def given_the_item_visibility_is_value(step, value):
    if world.using_selenium:
        world.browser.get(django.django_url("/dashboard/settings/"))

        if value == "Yes":
            elt = world.browser.find_element_by_id("item_visibility_yes")
            elt.click()
        else:
            elt = world.browser.find_element_by_id("item_visibility_no")
            elt.click()
            elt = world.browser.find_element_by_id("selection_visibility_no")
            elt.click()

        elt = world.browser.find_element_by_id("selection_visibility_submit")
        if elt:
            elt.click()
            world.browser.get(django.django_url("/"))


@step(u'I set the "([^"]*)" "([^"]*)" field to "([^"]*)"')
def i_set_the_label_ftype_to_value(step, label, ftype, value,
                                   sid='asset-view-details'):
    if world.using_selenium:
        parent = world.browser.find_element_by_id(sid)

        if ftype == "text":
            selector = "input[type=text]"
        elif ftype == "textarea":
            selector = "textarea"
        elts = parent.find_elements_by_css_selector(selector)
        for elt in elts:
            try:
                label_attr = elt.get_attribute('data-label')
            except StaleElementReferenceException:
                continue

            if label_attr == label:
                try:
                    elt.clear()
                    time.sleep(1)
                    elt.send_keys(value)
                    return
                except InvalidElementStateException:
                    time.sleep(1)
                    elt.clear()
                    time.sleep(1)
                    elt.send_keys(value)


@step(u'I remove the item tags')
def i_remove_the_item_tags(step):
    if world.using_selenium:
        selector = '.global-annotation-tags.select2-container'
        wait = WebDriverWait(world.browser, 10)
        parent = wait.until(
            visibility_of_element_located((By.CSS_SELECTOR, selector)))
        elts = parent.find_elements_by_css_selector(
            'a.select2-search-choice-close')
        for elt in elts:
            elt.click()


@step(u'I set the item tags to "([^"]*)"')
def i_set_the_item_tags_to_value(step, value):
    if world.using_selenium:
        sid = 'asset-view-details'
        sel = '.global-annotation-tags.select2-container input.select2-input'
        parent = world.browser.find_element_by_id(sid)
        elt = parent.find_element_by_css_selector(sel)
        elt.clear()
        elt.send_keys(value)
        elt.send_keys(Keys.ENTER)


@step(u'I insert "([^"]*)" into the text')
def i_insert_title_into_the_text(step, title):
    link = world.browser.find_element_by_partial_link_text(title)
    href = link.get_attribute("href")

    # strip the http://localhost:port off this href
    pieces = urlparse(href)

    insert_icon = world.browser.find_element_by_name(pieces.path)
    insert_icon.click()


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


@step(u'Contextual help is visible for the ([^"]*)')
def contextual_help_is_visible_for_the_area(step, area):
    eid = None
    if area == 'asset':
        eid = 'asset-view-help'
    elif area == 'collection':
        eid = 'collection-help'

    wait = ui.WebDriverWait(world.browser, 5)
    wait.until(visibility_of_element_located((By.ID, eid)))


@step(u'I close the ([^"]*)\'s contextual help')
def i_close_the_area_s_contextual_help(step, area):
    eid = None
    if area == 'asset':
        eid = 'asset-view-help'
    elif area == 'collection':
        eid = 'collection-help'

    elt = world.browser.find_element_by_id(eid)
    btn = elt.find_element_by_css_selector("input[type='button']")
    btn.click()


@step(u'Contextual help is not visible for the ([^"]*)')
def contextual_help_is_not_visible_for_the_area(step, area):
    eid = None
    if area == 'asset':
        eid = 'asset-view-help'
    elif area == 'collection':
        eid = 'collection-help'

    wait = ui.WebDriverWait(world.browser, 5)
    wait.until(invisibility_of_element_located((By.ID, eid)))


@step(u'I set the quickedit "([^"]*)" "([^"]*)" field to "([^"]*)"')
def i_set_the_quickedit_label_ftype_to_value(step, label, ftype, value):
    return i_set_the_label_ftype_to_value(step, label, ftype, value,
                                          sid='asset-view-details-quick-edit')


@step('there is a Create button')
def there_is_a_create_button(step):
    wait = ui.WebDriverWait(world.browser, 5)
    wait.until(visibility_of_element_located((By.ID, 'homepage-create-menu')))


@step('I click the Create button')
def i_click_the_create_button(step):
    wait = ui.WebDriverWait(world.browser, 5)
    the_id = 'homepage-create-menu'
    elt = wait.until(visibility_of_element_located((By.ID, the_id)))
    elt.click()


# Local utility functions
def get_column(title):
    selector = "//h2[contains(.,'{}')]/..".format(title)
    wait = ui.WebDriverWait(world.browser, 5)
    return wait.until(visibility_of_element_located((By.XPATH, selector)))


@step(u'When I view the "([^"]*)" asset')
def when_i_view_the_title_asset(step, title):
    item = Asset.objects.filter(title=title).first()
    url = reverse('asset-view', kwargs={'asset_id': item.id})
    world.browser.get(django.django_url(url))


def find_button_by_value(value, parent=None):

    if not parent:
        parent = world.browser

    selector = "input[type=submit][value='{}']".format(value)
    try:
        return parent.find_element_by_css_selector(selector)
    except NoSuchElementException:
        pass  # try something else

    selector = "input[type=button][value='{}']".format(value)
    try:
        return parent.find_element_by_css_selector(selector)
    except NoSuchElementException:
        pass  # try something else

    selector = "//button[contains(.,'{}')]".format(value)
    try:
        return parent.find_element_by_xpath(selector)
    except NoSuchElementException:
        pass  # try something else

    try:
        return parent.find_element_by_partial_link_text(value)
    except NoSuchElementException:
        pass  # try something else

    return None

world.find_button_by_value = find_button_by_value
