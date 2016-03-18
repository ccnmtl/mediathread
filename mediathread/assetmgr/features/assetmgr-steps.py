from lettuce import world, step
from selenium.webdriver.support.expected_conditions import \
    visibility_of_element_located
import selenium.webdriver.support.ui as ui
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException


@step(u'The item header is "([^"]*)"')
def the_item_header_is_name(step, name):
    if world.using_selenium:
        selector = '//span[@class="asset-view-title"][text()="{}"]'.format(
            name)
        wait = ui.WebDriverWait(world.browser, 5)
        elt = wait.until(visibility_of_element_located((By.XPATH, selector)))
        assert elt is not None


@step(u'I edit the item')
def i_edit_the_item(step):
    if world.using_selenium:
        elt = world.browser.find_element_by_css_selector(
            "#asset-view-details .edit-item-icon")
        elt.click()


@step(u'there is not a "([^"]*)" "([^"]*)" field')
def there_is_not_a_label_type_field(step, label, type):
    if world.using_selenium:
        if type == "text":
            selector = "#asset-view-details input[type=text][data-label='{}']"
        elif type == "textarea":
            selector = "#asset-view-details textarea[data-label='{}']"

        try:
            world.browser.find_element_by_css_selector(selector.format(label))
            assert False, "Found a %s %s field" % (label, type)
        except NoSuchElementException:
            pass


@step(u'the item has the tag "([^"]*)"')
def the_item_has_the_tag_group1(step, group1):
    sel = '#asset-header .meta.global-annotation-tags'
    elt = world.browser.find_element_by_css_selector(sel)
    print elt.text
    assert group1 in elt.text, '{} tag not found'.format(group1)


@step(u'the item does not have the tag "([^"]*)"')
def the_item_does_not_have_the_tag_group1(step, group1):
    sel = '#asset-header .meta.global-annotation-tags'
    elt = world.browser.find_element_by_css_selector(sel)
    assert group1 not in elt.text, '{} tag found'.format(group1)


@step(u'the item notes are "([^"]*)"')
def the_item_notes_are_group1(step, group1):
    selector = ("//*[@id='asset-view-details']"
                "//div[@class='global-annotation-notes']"
                "[contains(text(),'{}')]").format(group1)
    wait = ui.WebDriverWait(world.browser, 5)
    wait.until(visibility_of_element_located((By.XPATH, selector)))


@step(u'the item notes are not "([^"]*)"')
def the_item_notes_are_not_group1(step, group1):
    selector = ("//*[@id='asset-view-details']"
                "//div[@class='global-annotation-notes']"
                "[not(contains(text(),'{}'))]").format(group1)
    wait = ui.WebDriverWait(world.browser, 5)
    wait.until(visibility_of_element_located((By.XPATH, selector)))
