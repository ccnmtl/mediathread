from lettuce import world, step


@step(u'The item header is "([^"]*)"')
def the_item_header_is_name(step, name):
    if world.using_selenium:
        selector = "span.asset-view-title"
        elt = world.browser.find_element_by_css_selector(selector)
        assert elt.text == name, \
            "The title was %s. Expected %s" % (elt.text, name)
