from lettuce import world, step
import time
from selenium.common.exceptions import InvalidElementStateException


@step(u'The item header is "([^"]*)"')
def the_item_header_is_name(step, name):
    if world.using_selenium:
        selector = "span.asset-view-title"
        elt = world.browser.find_element_by_css_selector(selector)

        if elt.text.strip() != name:
            time.sleep(2)
            assert elt.text.strip() == name, \
                "The title was %s. Expected %s" % (elt.text, name)


@step(u'I edit the item')
def i_edit_the_item(step):
    if world.using_selenium:
        time.sleep(1)
        parent = world.browser.find_element_by_id("asset-view-details")
        selector = "input[type=image]"
        elts = parent.find_elements_by_css_selector(selector)
        for e in elts:
            if e.get_attribute('title') == "Edit item":
                e.click()
                return

    assert False, "Unable to find the edit item icon"


@step(u'I set the "([^"]*)" "([^"]*)" field to "([^"]*)"')
def i_set_the_label_type_to_value(step, label, type, value):
    if world.using_selenium:
        parent = world.browser.find_element_by_id("asset-view-details")
        if type == "text":
            selector = "input[type=text]"
        elif type == "textarea":
            selector = "textarea"
        elts = parent.find_elements_by_css_selector(selector)
        for elt in elts:
            if elt.get_attribute('data-label') == label:
                try:
                    elt.clear()
                    elt.send_keys(value)
                    return
                except InvalidElementStateException:
                    time.sleep(1)
                    elt.clear()
                    elt.send_keys(value)


@step(u'there is not a "([^"]*)" "([^"]*)" field')
def there_is_not_a_label_type_field(step, label, type):
    if world.using_selenium:
        parent = world.browser.find_element_by_id("asset-view-details")
        if type == "text":
            selector = "input[type=text]"
        elif type == "textarea":
            selector = "textarea"

        elts = parent.find_elements_by_css_selector(selector)
        for elt in elts:
            if elt.get_attribute('data-label') == label:
                assert False, "Found a %s %s field" % (label, type)
