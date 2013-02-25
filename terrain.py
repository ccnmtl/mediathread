# -*- coding: utf-8 -*-
from django.conf import settings
from django.test import client
from lettuce import before, after, world, step
from lettuce.django import django_url
from selenium.common.exceptions import StaleElementReferenceException
import errno
import os
import selenium.webdriver.support.ui as ui
import time

try:
    from lxml import html
    from selenium import webdriver
    from selenium.webdriver.firefox.firefox_profile import FirefoxProfile
except:
    pass


@before.each_scenario
def reset_database(variables):
    world.using_selenium = False

    try:
        os.remove('lettuce.db')
    except OSError, e:
        if e.errno != errno.ENOENT:  # errno.ENOENT = no such file or directory
            raise  # re-raise exception if a different error occurred
        else:
            pass  # database doesn't exist yet. that's okay.

    os.system('cp lettuce_base.db lettuce.db')


@before.all
def setup_browser():
    browser = getattr(settings, 'BROWSER', None)
    if browser is None:
        raise Exception('Please configure a browser in settings_test.py')
    elif browser == 'Firefox':
        ff_profile = FirefoxProfile()
        ff_profile.set_preference("webdriver_enable_native_events", False)
        world.browser = webdriver.Firefox(ff_profile)
    elif  browser == 'Chrome':
        world.browser = webdriver.Chrome()

    world.client = client.Client()
    world.using_selenium = False

    # Make the browser size at least 1024x768
    world.browser.execute_script("window.moveTo(0, 1); "
                                 "window.resizeTo(1024, 768);")

    # Wait implicitly for 2 seconds
    world.browser.implicitly_wait(5)

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


@step(r'I access the url "(.*)"')
def access_url(step, url):
    if world.using_selenium:
        world.browser.get(django_url(url))
    else:
        response = world.client.get(django_url(url))
        world.dom = html.fromstring(response.content)


@step(u'the ([^"]*) workspace is loaded')
def the_name_workspace_is_loaded(step, name):
    id = None
    if (name == "composition" or
        name == "assignment" or
            name == "home" or name == "collection"):
        id = "loaded"
    else:
        assert False, "No selector configured for %s" % name

    wait = ui.WebDriverWait(world.browser, 5)
    wait.until(lambda driver: world.browser.find_element_by_id(id))


@step(u'my browser resolution is ([^"]*) x ([^"]*)')
def my_browser_resolution_is_width_x_height(step, width, height):
    cmd = "window.moveTo(0, 1); window.resizeTo(%s, %s);" % (width, height)
    world.browser.execute_script(cmd)


@step(u'I am ([^"]*) in ([^"]*)')
def i_am_username_in_course(step, username, coursename):
    if world.using_selenium:
        world.browser.get(django_url("/accounts/logout/"))
        world.browser.get(django_url("accounts/login/?next=/"))
        username_field = world.browser.find_element_by_id("id_username")
        username_field.send_keys(username)

        password_field = world.browser.find_element_by_id("id_password")
        password_field.send_keys("test")

        form = world.browser.find_element_by_name("login_local")
        form.submit()

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
        world.browser.get(django_url("/accounts/logout/"))
    else:
        world.client.logout()


@step(u'I log out')
def i_log_out(step):
    if world.using_selenium:
        world.browser.get(django_url("/accounts/logout/"))
    else:
        response = world.client.get(django_url("/accounts/logout/"),
                                    follow=True)
        world.response = response
        world.dom = html.fromstring(response.content)


@step(u'I am at the ([^"]*) page')
def i_am_at_the_name_page(step, name):
    if world.using_selenium:
        wait = ui.WebDriverWait(world.browser, 5)
        wait.until(lambda driver: world.browser.title.find(name) > -1)


@step(u'there is a sample assignment')
def there_is_a_sample_assignment(step):
    os.system("./manage.py loaddata mediathread_main/fixtures/"
              "sample_assignment.json --settings=settings_test > /dev/null")
    time.sleep(2)


@step(u'there is a sample response')
def there_is_a_sample_response(step):
    os.system("./manage.py loaddata mediathread_main/fixtures/"
              "sample_assignment_and_response.json "
              "--settings=settings_test > /dev/null")
    time.sleep(2)


@step(u'I type "([^"]*)" for ([^"]*)')
def i_type_value_for_field(step, value, field):
    if world.using_selenium:
        selector = "input[name=%s]" % field
        input = world.browser.find_element_by_css_selector(selector)
        assert input is not None, "Cannot locate input field named %s" % field
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
            world.browser.find_element_by_partial_link_text(text)
            assert False, "found the '%s' link" % text
        except:
            pass  # expected


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
            link = world.browser.find_element_by_partial_link_text(text)
            assert link.is_displayed()
        except:
            world.browser.get_screenshot_as_file("/tmp/selenium.png")
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
            link = world.browser.find_element_by_partial_link_text(text)
            assert link.is_displayed()
            link.click()
        except:
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
def then_i_wait_count_seconds(step, count):
    n = int(count)
    time.sleep(n)


@step(u'I see "([^"]*)"')
def i_see_text(step, text):
    try:
        assert text in world.browser.page_source, world.browser.page_source
    except:
        time.sleep(1)
        msg = "I did not see %s in this page" % text
        assert text in world.browser.page_source, msg


@step(u'I do not see "([^"]*)"')
def i_do_not_see_text(step, text):
    assert text not in world.browser.page_source, world.browser.page_source


@step(u'I cancel an alert dialog')
def i_cancel_an_alert_dialog(step):
    time.sleep(1)
    alert = world.browser.switch_to_alert()
    alert.dismiss()
    time.sleep(1)


@step(u'I ok an alert dialog')
def i_ok_an_alert_dialog(step):
    time.sleep(1)
    alert = world.browser.switch_to_alert()
    alert.accept()
    time.sleep(1)


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
    except:
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
            except:
                return  # Expected outcome


@step(u'I\'m told ([^"]*)')
def i_m_told_text(step, text):
    alert = world.browser.switch_to_alert()
    assert alert.text.startswith(text), "Alert text invalid: %s" % alert.text
    alert.accept()


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

    assert column, "Unable to find a column entitled %s" % title

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
    column = get_column(title)
    if not column:
        selector = "td.panel-container.%s" % title.lower()
        column = world.browser.find_element_by_css_selector(selector)
    assert column, "Unable to find a column entitled %s" % title

    s = "div.switcher_collection_chooser"
    m = column.find_element_by_css_selector(s)
    owner = m.find_element_by_css_selector("a.switcher-top span.title")
    msg = "Expected owner title to be %s. Actually %s" % (name, owner.text)
    if owner.text != name:
        time.sleep(1)
        m = column.find_element_by_css_selector(s)
        owner = m.find_element_by_css_selector("a.switcher-top span.title")

    assert owner.text == name, msg


@step(u'the collection panel has a "([^"]*)" item')
def the_collection_panel_has_a_title_item(step, title):
    panel = get_column('collection')
    if not panel:
        selector = "td.panel-container.collection"
        panel = world.browser.find_element_by_css_selector(selector)

    assert panel, "Cannot find the collection panel"

    items = panel.find_elements_by_css_selector('div.gallery-item')
    for i in items:
        elt = i.find_element_by_css_selector('a.asset-title-link')
        if elt.text == title:
            return

    assert False, "Unable to find item [%s] in the collection panel" % title


@step(u'the collection panel has no "([^"]*)" item')
def the_collection_panel_has_no_title_item(step, title):
    panel = get_column('collection')
    if not panel:
        selector = "td.panel-container.collection"
        panel = world.browser.find_element_by_css_selector(selector)

    assert panel, "Cannot find the collection panel"

    items = panel.find_elements_by_css_selector('div.gallery-item')
    for i in items:
        elt = i.find_element_by_css_selector('a.asset-title-link')
        if elt.text == title:
            assert False, "Found an item [%s] in the collection panel" % title

    assert True, "Unable to find the %s item in the collection panel" % title


@step(u'the "([^"]*)" item has a note "([^"]*)"')
def the_title_item_has_a_note_text(step, title, text):
    panel = get_column('collection')
    if not panel:
        selector = "td.panel-container.collection"
        panel = world.browser.find_element_by_css_selector(selector)

    assert panel, "Cannot find the collection panel"

    items = panel.find_elements_by_css_selector('div.gallery-item')
    for i in items:
        elt = i.find_element_by_css_selector('a.asset-title-link')
        if elt.text == title:
            note = i.find_element_by_css_selector(
                'li.annotation-global-body span.metadata-value')
            assert note, "Unable to find a note for the %s item" % title
            assert note.text == text, ("Item note is %s. Expected %s" %
                                       (note.text, text))
            return

    assert False, "No named [%s] in the collection panel" % title


@step(u'the "([^"]*)" item has ([^"]*) selections, ([^"]*) by me')
def the_title_item_has_a_total_selections_count_by_me(step,
                                                      title,
                                                      total,
                                                      count):
    panel = get_column('collection')
    if not panel:
        selector = "td.panel-container.collection"
        panel = world.browser.find_element_by_css_selector(selector)

    assert panel, "Cannot find the collection panel"

    items = panel.find_elements_by_css_selector('div.gallery-item')
    for i in items:
        elt = i.find_element_by_css_selector('a.asset-title-link')
        if elt.text == title:
            item_total = i.find_element_by_css_selector(
                'span.item-annotation-count-total')
            msg = "Item selection count is %s. Expected %s" % (item_total.text,
                                                               total)
            assert item_total.text == total, msg

            my_count = i.find_element_by_css_selector(
                'span.item-annotation-count-user')

            msg = ("User item selection count is %s. Expected %s" %
                   (my_count.text, count))
            assert my_count.text == count, msg
            return

    assert False, "Unable to find item [%s] in the collection panel" % title


@step(u'the "([^"]*)" item has a tag "([^"]*)"')
def the_title_item_has_a_tag_text(step, title, text):
    panel = get_column('collection')
    if not panel:
        selector = "td.panel-container.collection"
        panel = world.browser.find_element_by_css_selector(selector)

    assert panel, "Cannot find the collection panel"

    items = panel.find_elements_by_css_selector('div.gallery-item')
    for i in items:
        elt = i.find_element_by_css_selector('a.asset-title-link')
        if elt.text == title:
            tags = i.find_elements_by_css_selector(
                'li.annotation-global-tags '
                'span.metadata-value a.switcher-choice')
            for t in tags:
                if t.text == text:
                    return
            assert False, "Unable to find a tag for the %s item" % title
            return

    assert False, "Unable to find item [%s] in the collection panel" % title


@step(u'the "([^"]*)" item has a selection "([^"]*)"')
def the_title_item_has_a_selection_seltitle(step, title, seltitle):
    panel = get_column('collection')
    if not panel:
        selector = "td.panel-container.collection"
        panel = world.browser.find_element_by_css_selector(selector)

    assert panel, "Cannot find the collection panel"

    select = 'td.selection-meta div.metadata-container a.materialCitationLink'

    items = panel.find_elements_by_css_selector('div.gallery-item')
    for i in items:
        elt = i.find_element_by_css_selector('a.asset-title-link')
        if elt.text == title:
            selection = i.find_element_by_css_selector(select)
            assert selection, "Unable to find the %s selection" % seltitle

            msg = "Selection title is %s. Expected %s" % (selection.text,
                                                          seltitle)
            assert selection.text == seltitle, msg

            return

    assert False, "Unable to find item [%s] in the collection panel" % title


@step(u'the "([^"]*)" item has no selections')
def the_title_item_has_no_selections(step, title):
    panel = get_column('collection')
    if not panel:
        selector = "td.panel-container.collection"
        panel = world.browser.find_element_by_css_selector(selector)

    assert panel, "Cannot find the collection panel"

    select = 'td.selection-meta div.metadata-container a.materialCitationLink'

    items = panel.find_elements_by_css_selector('div.gallery-item')
    for i in items:
        elt = i.find_element_by_css_selector('a.asset-title-link')
        if elt.text == title:
            try:
                selections = i.find_elements_by_css_selector(select)
                assert False, "Item %s has %s selections" % (title,
                                                             len(selections))
            except:
                return

    assert False, "Unable to find item [%s] in the collection panel" % title


@step(u'the "([^"]*)" item has no notes')
def the_title_item_has_no_notes(step, title):
    panel = get_column('collection')
    if not panel:
        selector = "td.panel-container.collection"
        panel = world.browser.find_element_by_css_selector(selector)

    assert panel, "Cannot find the collection panel"

    select = 'li.annotation-global-body span.metadata-value'

    items = panel.find_elements_by_css_selector('div.gallery-item')
    for i in items:
        elt = i.find_element_by_css_selector('a.asset-title-link')
        if elt.text == title:
            try:
                i.find_element_by_css_selector(select)
                assert False, "Item %s has notes" % title
            except:
                return

    assert False, "Unable to find item [%s] in the collection panel" % title


@step(u'the "([^"]*)" item has no tags')
def the_title_item_has_no_tags(step, title):
    panel = get_column('collection')
    if not panel:
        selector = "td.panel-container.collection"
        panel = world.browser.find_element_by_css_selector(selector)

    assert panel, "Cannot find the collection panel"
    select = 'li.annotation-global-tags span.metadata-value a.switcher-choice'

    items = panel.find_elements_by_css_selector('div.gallery-item')
    for i in items:
        elt = i.find_element_by_css_selector('a.asset-title-link')
        if elt.text == title:
            try:
                i.find_element_by_css_selector(select)
                assert False, "Item %s has tags" % title
            except:
                return

    assert False, "Unable to find item [%s] in the collection panel" % title


@step(u'the "([^"]*)" selection has a note "([^"]*)"')
def the_seltitle_selection_has_a_note_text(step, seltitle, text):
    panel = get_column('collection')
    if not panel:
        selector = "td.panel-container.collection"
        panel = world.browser.find_element_by_css_selector(selector)

    assert panel, "Cannot find the collection panel"

    selections = panel.find_elements_by_css_selector('td.selection-meta')
    for s in selections:
        title = s.find_element_by_css_selector(
            'div.metadata-container a.materialCitationLink')
        if title and title.text == seltitle:
            note = s.find_element_by_css_selector(
                'div.annotation-notes span.metadata-value')

            assert note, "No note for the %s selection" % seltitle

            msg = "The %s note reads %s. Expected %s" % (seltitle,
                                                         note.text,
                                                         text)
            assert note.text == text, msg

            return

    assert False, "No selection [%s] in the collection panel" % seltitle


@step(u'the "([^"]*)" selection has a tag "([^"]*)"')
def the_seltitle_selection_has_a_tag_text(step, seltitle, text):
    panel = get_column('collection')
    if not panel:
        selector = "td.panel-container.collection"
        panel = world.browser.find_element_by_css_selector(selector)

    assert panel, "Cannot find the collection panel"

    selections = panel.find_elements_by_css_selector('td.selection-meta')
    for s in selections:
        title = s.find_element_by_css_selector(
            'div.metadata-container a.materialCitationLink')
        if title and title.text == seltitle:
            tags = s.find_elements_by_css_selector(
                'div.annotation-tags span.metadata-value a.switcher-choice')
            for t in tags:
                if t.text == text:
                    return
            assert False, "No tag for the %s selection" % seltitle
            return

    assert False, "No selection [%s] in the collection panel" % seltitle


@step(u'the "([^"]*)" item has an? ([^"]*) icon')
def the_title_item_has_a_type_icon(step, title, type):
    select = "div.gallery-item"
    items = world.browser.find_elements_by_css_selector(select)
    for item in items:
        try:
            item.find_element_by_partial_link_text(title)
        except:
            continue

        try:
            item.find_element_by_css_selector("a.%s-asset" % type)
            return  # found the link & the icon
        except:
            try:
                item.find_element_by_css_selector("a.%s-asset-inplace" % type)
                return  # found the link & the icon
            except:
                assert False, \
                    "Item %s does not have a %s icon." % (title, type)

    assert False, "Unable to find the %s item" % title


@step(u'the "([^"]*)" item has no ([^"]*) icon')
def the_title_item_has_no_type_icon(step, title, type):
    select = "div.gallery-item"
    items = world.browser.find_elements_by_css_selector(select)
    for item in items:
        try:
            item.find_element_by_partial_link_text(title)
        except:
            continue

        try:
            item.find_element_by_css_selector("a.%s-asset" % type)
            assert False, "Item %s has a %s icon." % (title, type)
        except:
            assert True, "Item %s does not have a %s icon" % (title, type)
            return

    assert False, "Unable to find the %s item" % title


@step(u'I click the "([^"]*)" item ([^"]*) icon')
def i_click_the_title_item_type_icon(step, title, type):
    time.sleep(1)
    select = "div.gallery-item"
    items = world.browser.find_elements_by_css_selector(select)
    for item in items:
        try:
            item.find_element_by_partial_link_text(title)
        except:
            continue

        try:
            if type == "delete":
                icon = item.find_element_by_css_selector(".%s_icon" % type)
            elif type == "edit":
                s = "a.%s-asset-inplace" % type
                icon = item.find_element_by_css_selector(s)

            icon.click()
            return  # found the link & the icon
        except:
            assert False, "Item %s does not have a %s icon." % (title, type)

    assert False, "Unable to find the %s item" % title


@step(u'I can filter by "([^"]*)" in the ([^"]*) column')
def i_can_filter_by_tag_in_the_title_column(step, tag, title):
    column = get_column(title)
    if not column:
        selector = "td.panel-container.%s" % title.lower()
        column = world.browser.find_element_by_css_selector(selector)

    assert column, "Unable to find a column entitled %s" % title

    filter_menu = column.find_element_by_css_selector(
        "div.switcher.collection-filter a.switcher-top")
    filter_menu.click()

    tags = column.find_elements_by_css_selector(
        "div.switcher.collection-filter a.switcher-choice.filterbytag")

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
        selector = "td.panel-container.%s" % title.lower()
        column = world.browser.find_element_by_css_selector(selector)
    assert column, "Unable to find a column entitled %s" % title

    filter_menu = column.find_element_by_css_selector(
        "div.switcher.collection-filter a.switcher-top")
    filter_menu.click()

    tags = column.find_elements_by_css_selector(
        "div.switcher.collection-filter a.switcher-choice.filterbytag")

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
        selector = "td.panel-container.%s" % title.lower()
        column = world.browser.find_element_by_css_selector(selector)
    assert column, "Unable to find a column entitled %s" % title

    elt = column.find_element_by_css_selector("a.switcher-choice.remove")
    elt.click()
    time.sleep(2)


@step(u'Given publish to world is ([^"]*)')
def given_publish_to_world_is_value(step, value):
    if world.using_selenium:
        ff = world.browser
        world.browser.get(django_url("/dashboard/settings/"))

        if value == "enabled":
            elt = ff.find_element_by_id('allow_public_compositions_yes')
            elt.click()
        else:
            elt = ff.find_element_by_id('allow_public_compositions_no')
            elt.click()

        elt = ff.find_element_by_id("allow_public_compositions_submit")
        if elt:
            elt.click()
            alert = ff.switch_to_alert()
            alert.accept()

            ff.get(django_url("/"))


@step(u'Then publish to world is ([^"]*)')
def then_publish_to_world_is_value(step, value):
    if value == 'enabled':
        elt = world.browser.find_element_by_id('allow_public_compositions_yes')
    else:
        elt = world.browser.find_element_by_id('allow_public_compositions_no')

    msg = "The checked attribute was %s" % elt.get_attribute("checked")
    assert elt.get_attribute('checked'), msg


@step(u'I cannot filter by "([^"]*)" in the ([^"]*) column')
def i_cannot_filter_by_tag_in_the_title_column(step, tag, title):
    column = get_column(title)
    if not column:
        selector = "td.panel-container.%s" % title.lower()
        column = world.browser.find_element_by_css_selector(selector)
    assert column, "Unable to find a column entitled %s" % title

    filter_menu = column.find_element_by_css_selector(
        "div.switcher.collection-filter")
    assert filter_menu
    filter_menu.click()

    try:
        tags = filter_menu.find_element_by_css_selector(
            "a.switcher-choice.filterbytag")
        for t in tags:
            if t.text == tag:
                assert False, "Found %s tag" % tag
    except:
        # pass - there may be no tags
        return


@step(u'The "([^"]*)" project has no delete icon')
def the_title_project_has_no_delete_icon(step, title):
    time.sleep(1)
    link = world.browser.find_element_by_partial_link_text(title)
    try:
        link.parent.find_element_by_css_selector(".delete_icon")
        assert False, "%s does have a delete icon" % title
    except:
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
    panel = world.browser.find_element_by_css_selector(selector)
    assert panel is not None, "Can't find panel named %s" % panel


@step(u'I call the ([^"]*) "([^"]*)"')
def i_call_the_panel_title(step, panel, title):
    selector = "td.panel-container.open.%s" % panel.lower()
    panel = world.browser.find_element_by_css_selector(selector)
    assert panel is not None, "Can't find panel named %s" % panel

    input = panel.find_element_by_name("title")
    input.clear()
    input.send_keys(title)


@step(u'I write some text for the ([^"]*)')
def i_write_some_text_for_the_panel(step, panel):
    selector = "td.panel-container.open.%s" % panel.lower()
    panel = world.browser.find_element_by_css_selector(selector)
    assert panel is not None, "Can't find panel named %s" % panel

    frame = panel.find_element_by_tag_name("iframe")
    world.browser.switch_to_frame(frame)
    input = world.browser.find_element_by_class_name("mceContentBody")
    input.send_keys("""The Columbia Center for New Teaching and Learning
                     was (CCNMTL) was founded at Columbia University in 1999
                     to enhance teaching and learning through the purposeful
                     use of new media and technology""")

    world.browser.switch_to_default_content()


@step(u'there is an? ([^"]*) "([^"]*)" reply by ([^"]*)')
def there_is_a_status_title_reply_by_author(step, status, title, author):
    selector = "div.assignment-listitem.response"
    elts = world.browser.find_elements_by_css_selector(selector)
    assert len(elts) > 0, "Expected at least 1 response. 0 found"

    for e in elts:
        title_elt = e.find_element_by_css_selector("a.metadata-value-response")
        title_parent = title_elt.parent

        if title_elt.text.strip() == title:
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
        except:
            title_elt = e.find_element_by_css_selector(
                "a.asset_title.type-assignment")
            assignment = True

        if title_elt.text.strip() == title:
            # type
            if assignment:
                type_elt = e.find_element_by_css_selector(
                    "span.metadata-value-assignment")
                assert type_elt.text.strip() == "ASSIGNMENT"
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

            return

    assert False, "Unable to find project named %s" % title


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
            time.sleep(1)
            return

    assert False, "Unable to locate the dialog's save button"


@step(u'Given the selection visibility is set to "([^"]*)"')
def given_the_selection_visibility_is_value(step, value):
    if world.using_selenium:
        world.browser.get(django_url("/dashboard/settings/"))

        if value == "Yes":
            elt = world.browser.find_element_by_id("selection_visibility_yes")
            elt.click()
        else:
            elt = world.browser.find_element_by_id("selection_visibility_no")
            elt.click()

        elt = world.browser.find_element_by_id("selection_visibility_submit")
        if elt:
            elt.click()
            alert = world.browser.switch_to_alert()
            alert.accept()

            world.browser.get(django_url("/"))


# Local utility functions
def get_column(title):
    elts = world.browser.find_elements_by_tag_name("h2")
    for e in elts:
        try:
            if e.text and e.text.strip().lower().find(title.lower()) > -1:
                return e.parent
        except StaleElementReferenceException:
            continue

    return None


def find_button_by_value(value, parent=None):

    if not parent:
        parent = world.browser

    elts = parent.find_elements_by_css_selector("input[type=submit]")
    for e in elts:
        if e.get_attribute("value") == value:
            return e

    elts = parent.find_elements_by_css_selector("input[type=button]")
    for e in elts:
        if e.get_attribute("value") == value:
            return e

    elts = world.browser.find_elements_by_tag_name("button")
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
