from lettuce import world, step
from lettuce.django import django_url
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.support.select import Select
from selenium.webdriver.support.expected_conditions import \
    visibility_of_element_located
import selenium.webdriver.support.ui as ui
from selenium.webdriver.common.by import By


@step(u'video upload is enabled')
def video_upload_is_enabled(step):
    if world.using_selenium:
        world.browser.get(django_url("/dashboard/sources/"))
        try:
            elt = world.browser.find_element_by_id("mediathread-video-upload")
            if elt:
                elt.click()
        except NoSuchElementException:
            pass  # It's already enabled. That's ok.


@step(u'I see ([0-9][0-9]?) sources?')
def i_see_count_source(step, count):
    if world.using_selenium:
        elts = world.browser.find_elements_by_css_selector(
            "div.recommend_source")
        assert len(elts) == int(count), \
            "Expected %s. Actually found %s" % (count, len(elts))


@step(u'I add YouTube to the class')
def when_i_add_youtube_to_the_class(step):
    if world.using_selenium:
        elt = world.browser.find_element_by_id("you-tube")
        elt.click()


@step(u'I allow ([^"]*)s to upload videos')
def i_allow_level_to_upload_videos(step, level):
    elt = world.browser.find_element_by_name('upload_permission')
    assert elt is not None, "Select element not found %s" % 'upload_permission'

    select = Select(elt)
    select.select_by_visible_text(level)

    form = world.browser.find_element_by_name("form-upload-permission")
    form.submit()


@step(u'The selection visibility is "([^"]*)"')
def the_selection_visibility_is_value(step, value):
    if value == 'Yes':
        elt = world.browser.find_element_by_id('selection_visibility_yes')
    else:
        elt = world.browser.find_element_by_id('selection_visibility_no')

    assert elt.get_attribute('checked'), \
        "The checked attribute was %s" % elt.get_attribute("checked")


@step(u'I can upload on behalf of other users')
def i_can_upload_on_behalf_of_other_users(step):
    world.browser.find_element_by_id('video_owners')


@step(u'I cannot upload on behalf of other users')
def i_cannot_upload_on_behalf_of_other_users(step):
    try:
        world.browser.find_element_by_id('video_owners')
        assert False, "This user can upload on behalf of other users"
    except NoSuchElementException:
        pass  # expected


@step(u'There is not an "Upload From Computer" feature')
def there_is_not_an_upload_from_computer_feature(step):
    try:
        world.browser.find_element_by_id('upload-from-computer')
        assert False, "Found an Upload From Computer menu link"
    except NoSuchElementException:
        pass  # expected


@step(u'There is an "Upload From Computer" feature')
def there_is_an_upload_from_computer_feature(step):
    wait = ui.WebDriverWait(world.browser, 5)
    wait.until(visibility_of_element_located((By.ID, 'upload-from-computer')))


@step('I open the "Upload From Computer" feature')
def i_open_the_upload_from_computer_feature(step):
    try:
        elt = world.browser.find_element_by_id('upload-from-computer')
        h3 = elt.find_element_by_tag_name('h3')
        h3.click()
    except NoSuchElementException:
        assert False, "Cannot find the Upload From Computer link"
        return
