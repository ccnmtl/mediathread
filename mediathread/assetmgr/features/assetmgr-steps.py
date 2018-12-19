from lettuce import world, step
from selenium.webdriver.support.expected_conditions import \
    visibility_of_element_located, invisibility_of_element_located, \
    presence_of_element_located
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
    print(elt.text)
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


@step(u'the "([^"]*)" item has no selections')
def the_title_item_has_no_selections(step, title):
    selector = (
        "//div[contains(@class,'gallery-item')]"
        "//a[contains(@class,'asset-title-link')][contains(text(),'{}')]/../.."
        "//span[contains(@class, 'item-annotation-count-total')][text()=0]"
        ).format(title)
    wait = ui.WebDriverWait(world.browser, 5)
    wait.until(visibility_of_element_located((By.XPATH, selector)))


@step(u'the "([^"]*)" item has ([^"]*) selections, ([^"]*) by me')
def the_title_item_has_a_total_selections_count_by_me(step, title,
                                                      total, count):

    selector = (
        "//div[contains(@class,'gallery-item')]"
        "//a[contains(@class,'asset-title-link')][contains(text(),'{}')]/../.."
        "//span[contains(@class, 'item-annotation-count-total')][text()={}]"
        ).format(title, total)
    wait = ui.WebDriverWait(world.browser, 5)
    wait.until(visibility_of_element_located((By.XPATH, selector)))

    selector = (
        "//tr[@class='asset-workspace-content-row']"
        "//div[contains(@class,'gallery-item')]"
        "//a[contains(@class,'asset-title-link')][contains(text(),'{}')]/../.."
        "//span[contains(@class, 'item-annotation-count-user')][text()={}]"
        ).format(title, count)
    wait = ui.WebDriverWait(world.browser, 5)
    wait.until(visibility_of_element_located((By.XPATH, selector)))


@step(u'the "([^"]*)" item has no ([^"]*) icon')
def the_title_item_has_no_name_icon(step, title, name):
    select = "div.gallery-item"
    items = world.browser.find_elements_by_css_selector(select)
    for item in items:
        try:
            item.find_element_by_partial_link_text(title)
        except NoSuchElementException:
            continue

        try:
            item.find_element_by_css_selector("a.%s-asset" % name)
            assert False, "Item %s has a %s icon." % (title, name)
        except NoSuchElementException:
            assert True, "Item %s does not have a %s icon" % (title, name)
            return

    assert False, "Unable to find the %s item" % title


@step(u'I can filter by "([^"]*)" in the Collection column')
def i_can_filter_by_tag_in_the_collection_column(step, tag):
    selector = "div.course-tags input"
    filter_menu = world.browser.find_element_by_css_selector(selector)
    filter_menu.click()

    selector = (
        "//ul[contains(@class,'select2-results')]"
        "/li/div[contains(.,'{}')]").format(tag)

    wait = ui.WebDriverWait(world.browser, 5)
    elt = wait.until(presence_of_element_located((By.XPATH, selector)))
    elt.click()

    wait = ui.WebDriverWait(world.browser, 5)
    wait.until(invisibility_of_element_located((By.CSS_SELECTOR,
                                                '.ajaxloader')))


@step(u'I clear all tags')
def i_clear_all_tags(step):
    wait = ui.WebDriverWait(world.browser, 5)
    selector = "a.select2-search-choice-close"
    for tag in world.browser.find_elements_by_css_selector(selector):
        tag = world.browser.find_element_by_css_selector(selector)
        tag.click()
        wait.until(invisibility_of_element_located((By.CSS_SELECTOR,
                                                    '.ajaxloader')))

    elts = world.browser.find_elements_by_css_selector(selector)
    assert True, len(elts) == 0
