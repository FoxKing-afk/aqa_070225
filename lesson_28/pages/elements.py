#!/usr/bin/python3
# -*- encoding=utf8 -*-

import time

from selenium.common import exceptions as EXCEPT
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.select import Select
from selenium.webdriver.support.ui import WebDriverWait




class WebElement():

    _locator = ('', '')
    _web_driver = None
    _page = None
    _timeout = 10
    _wait_after_click = False  # TODO: how we can wait after click?

    def __init__(self, timeout=10, wait_after_click=False, **kwargs):
        self._timeout = timeout
        self._wait_after_click = wait_after_click

        for by, locate in kwargs.items():
            if by == 'driver':
                self._web_driver = locate
            elif by == 'xpath':
                self._locator = (By.XPATH, locate)
            # elif by == 'css':
            #     self._locator = (By.CSS_SELECTOR, locate)

    def find(self, timeout=10):
        """ Find element on the page. """

        element = None

        try:
            element = WebDriverWait(self._web_driver, timeout).until(
               EC.presence_of_element_located(self._locator)
            )
        except (EXCEPT.WebDriverException, EXCEPT.JavascriptException):
            print(('Element not found on the page!', 'red'))

        return element

    def wait_to_be_clickable(self, timeout=10, check_visibility=True):
        """ Wait until the element will be ready for click. """

        element = None

        try:
            element = WebDriverWait(self._web_driver, timeout).until(
                EC.element_to_be_clickable(self._locator)
            )
        except:
            print(('Element not clickable!', 'red'))

        if check_visibility:
            self.wait_until_not_visible()

        return element

    def is_clickable(self):
        """ Check is element ready for click or not. """

        element = self.wait_to_be_clickable(timeout=0.1)
        return element is not None

    def is_presented(self):
        """ Check that element is presented on the page. """

        element = self.find(timeout=0.1)
        return element is not None

    def is_visible(self):
        """ Check is the element visible or not. """

        element = self.find(timeout=1)

        if element:
            return element.is_displayed()

        return False

    def wait_until_not_visible(self, timeout=10):

        element = None

        try:
            element = WebDriverWait(self._web_driver, timeout).until(
                EC.visibility_of_element_located(self._locator)
            )
        except:
            print(('Element not visible!', 'red'))

        if element:
            js = ('return (!(arguments[0].offsetParent === null) && '
                  '!(window.getComputedStyle(arguments[0]) === "none") &&'
                  'arguments[0].offsetWidth > 0 && arguments[0].offsetHeight > 0'
                  ');')
            visibility = self._web_driver.execute_script(js, element)
            iteration = 0

            while not visibility and iteration < 10:
                time.sleep(0.5)

                iteration += 1

                visibility = self._web_driver.execute_script(js, element)
                print('Element {0} visibility: {1}'.format(self._locator, visibility))

        return element

    def send_keys(self, keys, wait=0.5):
        """ Send keys to the element. """

        keys = keys.replace('\n', '\ue007')

        element = self.find()

        if element:
            element.clear()
            element.send_keys(keys)
            time.sleep(wait)
        else:
            msg = 'Element with locator {0} not found'
            raise AttributeError(msg.format(self._locator))

    def get_text(self):
        """ Get text of the element. """

        element = self.find()
        text = ''

        try:
            text = str(element.text)
        except Exception as e:
            print('Error: {0}'.format(e))

        return text

    def get_attribute(self, attr_name):
        """ Get attribute of the element. """

        element = self.find()

        if element:
            return element.get_attribute(attr_name)

    def _set_value(self, web_driver, value, clear=True):
        """ Set value to the input element. """

        element = self.find()

        if clear:
            element.clear()

        element.send_keys(value)

    def click(self, hold_seconds=0, x_offset=1, y_offset=1):
        """ Wait and click the element. """

        element = self.wait_to_be_clickable()

        if element:
            action = ActionChains(self._web_driver)
            action.move_to_element_with_offset(element, x_offset, y_offset).\
                pause(hold_seconds).click(on_element=element).perform()
        else:
            msg = 'Element with locator {0} not found'
            raise AttributeError(msg.format(self._locator))

        if self._wait_after_click:
            self._page.wait_page_loaded()

    def right_mouse_click(self, x_offset=0, y_offset=0, hold_seconds=0):
        """ Click right mouse button on the element. """

        element = self.wait_to_be_clickable()

        if element:
            action = ActionChains(self._web_driver)
            action.move_to_element_with_offset(element, x_offset, y_offset). \
                pause(hold_seconds).context_click(on_element=element).perform()
        else:
            msg = 'Element with locator {0} not found'
            raise AttributeError(msg.format(self._locator))

    def highlight_and_make_screenshot(self, file_name='element.png'):
        """ Highlight element and make the screen-shot of all page. """

        element = self.find()

        # Scroll page to the element:
        self._web_driver.execute_script("arguments[0].scrollIntoView();", element)

        # Add red border to the style:
        self._web_driver.execute_script("arguments[0].style.border='3px solid red';", element)

        # Make screen-shot of the page:
        self._web_driver.save_screenshot(file_name)

    def scroll_to_element(self):
        """ Scroll page to the element. """

        element = self.find()

        # Scroll page to the element (option #1):
        self._web_driver.execute_script("arguments[0].scrollIntoView();", element)
        
        # Scroll to element (option #2 - sometimes it is only one working solution)
        # element.send_keys(Keys.DOWN)

    def delete(self):
        """ Deletes element from the page. """

        element = self.find()

        # Delete element:
        self._web_driver.execute_script("arguments[0].remove();", element)
    
    def select(self, text: str):
        """ Select element from the selector """

        select_element = self.find()
        _select = Select(select_element)
        _select.select_by_visible_text(text)



class ManyWebElements(WebElement):

    def __getitem__(self, item):
        """ Get list of elements and try to return required element. """

        elements = self.find()
        return elements[item]

    def find(self, timeout=10):
        """ Find elements on the page. """

        elements = []

        try:
            elements = WebDriverWait(self._web_driver, timeout).until(
               EC.presence_of_all_elements_located(self._locator)
            )
        except:
            print(('Elements not found on the page!', 'red'))

        return elements

    def _set_value(self, web_driver, value):
        """ Note: this action is not applicable for the list of elements. """
        raise NotImplemented('This action is not applicable for the list of elements')

    def click(self, hold_seconds=0, x_offset=0, y_offset=0):
        """ Note: this action is not applicable for the list of elements. """
        raise NotImplemented('This action is not applicable for the list of elements')

    def count(self):
        """ Get count of elements. """

        elements = self.find()
        return len(elements)

    def get_text(self):
        """ Get text of elements. """

        elements = self.find()
        result = []

        for element in elements:
            text = ''

            try:
                text = str(element.text)
            except Exception as e:
                print('Error: {0}'.format(e))

            result.append(text)

        return result

    def get_attribute(self, attr_name):
        """ Get attribute of all elements. """

        results = []
        elements = self.find()

        for element in elements:
            results.append(element.get_attribute(attr_name))

        return results

    def highlight_and_make_screenshot(self, file_name='element.png'):
        """ Highlight elements and make the screen-shot of all page. """

        elements = self.find()

        for element in elements:
            # Scroll page to the element:
            self._web_driver.execute_script("arguments[0].scrollIntoView();", element)

            # Add red border to the style:
            self._web_driver.execute_script("arguments[0].style.border='3px solid red'", element)

        # Make screen-shot of the page:
        self._web_driver.save_screenshot(file_name)


if __name__ == "__main__":
    import sys
    import pathlib
    import time
    root = str(pathlib.Path(__file__).parent.parent)
    sys.path.insert(0, root)
    from get_browser import firefox
    driver = firefox(True)
    url = "https://guest:welcome2qauto@qauto.forstudy.space/"
    driver.get(url)
    _menu_home = '//a[text()="Home"]'
    elment = WebElement(xpath=_menu_home, driver=driver)
    print(elment.is_clickable())
    print(elment.is_presented())
    print(elment.is_visible())
    driver.close()