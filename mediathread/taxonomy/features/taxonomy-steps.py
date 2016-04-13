from lettuce import world, step, django
from selenium.webdriver.support.expected_conditions import \
    invisibility_of_element_located, visibility_of_element_located
import selenium.webdriver.support.ui as ui
from selenium.webdriver.common.by import By


@step(u'I create the concept')
def i_create_the_concept(step):
    selector = ".create-vocabulary-submit"
    elt = world.browser.find_element_by_css_selector(selector)
    elt.click()


@step(u'I save the concept')
def i_save_the_concept(step):
    parent = world.browser.find_element_by_css_selector('div.vocabulary-edit')
    selector = ".edit-vocabulary-submit"
    elt = parent.find_element_by_css_selector(selector)
    elt.click()


@step(u'I create a new concept')
def i_create_a_new_concept(step):
    selector = 'a.create-vocabulary-open'
    elt = world.browser.find_element_by_css_selector(selector)
    elt.click()


@step(u'I name the concept "([^"]*)"')
def i_name_the_concept_title(step, title):
    selector = 'input.create-vocabulary-name'
    wait = ui.WebDriverWait(world.browser, 5)
    wait.until(visibility_of_element_located((By.CSS_SELECTOR, selector)))

    elt = world.browser.find_element_by_css_selector(selector)
    elt.clear()
    elt.send_keys(title)


@step(u'the "([^"]*)" concept has a delete icon')
def the_group1_concept_has_a_delete_icon(step, group1):
    link = world.browser.find_element_by_partial_link_text(group1)
    parent = link.parent

    icon = parent.find_element_by_css_selector('a.delete-vocabulary')
    assert icon, "Unable to find a delete icon for %s" % group1


@step(u'I click the "([^"]*)" concept delete icon')
def i_click_the_group1_concept_delete_icon(step, group1):
    link = world.browser.find_element_by_partial_link_text(group1)
    parent = link.parent

    icon = parent.find_element_by_css_selector('a.delete-vocabulary')
    assert icon, "Unable to find a delete icon for %s" % group1
    icon.click()


@step(u'the "([^"]*)" concept has an edit icon')
def the_group1_concept_has_an_edit_icon(step, group1):
    link = world.browser.find_element_by_partial_link_text(group1)
    parent = link.parent

    icon = parent.find_element_by_css_selector('a.edit-vocabulary-open')
    assert icon, "Unable to find an edit icon for %s" % group1


@step(u'I click the "([^"]*)" concept edit icon')
def i_click_the_group1_concept_edit_icon(step, group1):
    link = world.browser.find_element_by_partial_link_text(group1)
    parent = link.parent

    icon = parent.find_element_by_css_selector('a.edit-vocabulary-open')
    assert icon, "Unable to find an edit icon for %s" % group1
    icon.click()


@step(u'I rename the "([^"]*)" concept to "([^"]*)"')
def i_rename_the_group1_concept_to_group2(step, group1, group2):
    parent = world.browser.find_element_by_css_selector('div.vocabulary-edit')

    elt = parent.find_element_by_name('display_name')
    elt.clear()
    elt.send_keys(group2)


@step(u'I name a term "([^"]*)"')
def i_name_a_term_group1(step, group1):
    elt = world.browser.find_element_by_name('term_name')
    elt.clear()
    elt.send_keys(group1)


@step(u'create the term')
def create_the_term(step):
    selector = ".create-term-submit"
    elt = world.browser.find_element_by_css_selector(selector)
    elt.click()


@step(u'I see a "([^"]*)" term')
def i_see_a_group1_term(step, group1):
    selector = "div.term-display h5"
    elts = world.browser.find_elements_by_css_selector(selector)
    for elt in elts:
        if elt.text == group1:
            return  # found it
    assert False, 'Unable to find the %s term' % group1


@step(u'I click the "([^"]*)" term delete icon')
def i_click_the_group1_term_delete_icon(step, group1):
    elts = world.browser.find_elements_by_css_selector('.term-display')
    for elt in elts:
        term = elt.find_element_by_css_selector('h5')
        if term.text == group1:
            icon = elt.find_element_by_css_selector('.delete-term')
            icon.click()
            return

    assert False, 'Unable to find the %s term delete icon' % group1


@step(u'I click the "([^"]*)" term edit icon')
def i_click_the_group1_term_edit_icon(step, group1):
    selector = "div.term-display h5"
    elts = world.browser.find_elements_by_css_selector(selector)
    for elt in elts:
        if elt.text == group1:
            parent = elt.parent
            icon = parent.find_element_by_css_selector('.edit-term-open')
            icon.click()
            return

    assert False, 'Unable to find the %s term delete icon' % group1


@step(u'I rename the "([^"]*)" term to "([^"]*)"')
def i_rename_the_group1_term_to_group2(step, group1, group2):
    selector = "input[name='term_name']"
    elts = world.browser.find_elements_by_css_selector(selector)
    for e in elts:
        if e.get_attribute("value") == group1:
            e.clear()
            e.send_keys(group2)
            return

    assert False, 'Unable to find the %s term' % group1


@step(u'I wait until the "([^"]*)" rename is complete')
def i_wait_until_the_name_rename_is_complete(step1, name):
    selector = "input[name='term_name'][value='" + name + "']"
    wait = ui.WebDriverWait(world.browser, 5)
    wait.until(invisibility_of_element_located((By.CSS_SELECTOR, selector)))


@step(u'I save the term')
def i_save_the_term(step):
    selector = '.edit-term-submit'
    elt = world.browser.find_element_by_css_selector(selector)
    elt.click()


@step(u'there is a "([^"]*)" term')
def there_is_a_name_term(step1, name):
    selector = '[data-id="%s"]' % name
    wait = ui.WebDriverWait(world.browser, 5)
    wait.until(visibility_of_element_located((By.CSS_SELECTOR, selector)))


@step(u'there is no "([^"]*)" term')
def there_is_no_name_term(step, name):
    selector = "div.term-display h5"
    elts = world.browser.find_elements_by_css_selector(selector)
    for elt in elts:
        if elt.text == name:
            assert False, 'Found the %s term' % name


@step(u'specify the onomy url')
def specify_the_onomy_url(step):
    url = django.django_url('/media/onomy/test.json')
    elt = world.browser.find_element_by_id('onomy_url')
    elt.send_keys(url)


@step(u'confirm the onomy import')
def confirm_the_onomy_import(step):
    selector = 'a.import-vocabulary-submit'
    elt = world.browser.find_element_by_css_selector(selector)
    elt.click()


@step(u'specify the incorrect onomy url')
def specify_the_incorrect_onomy_url(step):
    url = django.django_url('incorrect')
    elt = world.browser.find_element_by_id('onomy_url')
    elt.send_keys(url)


@step(u'specify the refresh onomy url')
def specify_the_refresh_onomy_url(step):
    url = django.django_url('/media/onomy/reimport_test.json')
    elt = world.browser.find_element_by_id('onomy_url')
    elt.send_keys(',')
    elt.send_keys(url)


@step(u'there is a "([^"]*)" concept')
def there_is_a_text_concept(step, text):
    wait = ui.WebDriverWait(world.browser, 6)
    wait.until(visibility_of_element_located((By.PARTIAL_LINK_TEXT,
                                              text)))


@step(u'there is not a "([^"]*)" concept')
def there_is_not_a_text_concept(step, text):
    wait = ui.WebDriverWait(world.browser, 5)
    wait.until(invisibility_of_element_located((By.PARTIAL_LINK_TEXT,
                                                text)))


@step(u'I click the "([^"]*)" concept')
def i_click_the_text_concept(step, text):
    wait = ui.WebDriverWait(world.browser, 5)
    elt = wait.until(visibility_of_element_located((By.PARTIAL_LINK_TEXT,
                                                    text)))
    elt.click()
