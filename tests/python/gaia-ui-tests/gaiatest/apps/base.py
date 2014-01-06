# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

from marionette.by import By
from marionette.errors import NoSuchElementException
from marionette.errors import StaleElementException
from marionette.wait import Wait

from gaiatest import GaiaApps
from gaiatest import GaiaData
from gaiatest import Accessibility


class Base(object):

    def __init__(self, marionette):
        self.marionette = marionette
        self.apps = GaiaApps(self.marionette)
        self.data_layer = GaiaData(self.marionette)
        self.accessibility = Accessibility(self.marionette)
        self.frame = None

    def launch(self, launch_timeout=None):
        self.app = self.apps.launch(self.name, launch_timeout=launch_timeout)

    def wait_for_element_present(self, by, locator, timeout=None):
        # TODO: Remove when we're using a version of Marionette with bug 957248 fixed
        timeout = timeout or (self.marionette.timeout and self.marionette.timeout / 1000.0) or 30
        return Wait(self.marionette, timeout, ignored_exceptions=NoSuchElementException).until(
            lambda m: m.find_element(by, locator))

    def wait_for_element_not_present(self, by, locator, timeout=None):
        if self.is_element_present:
            # TODO: Remove when we're using a version of Marionette with bug 957248 fixed
            timeout = timeout or (self.marionette.timeout and self.marionette.timeout / 1000.0) or 30
            try:
                return Wait(self.marionette, timeout).until(
                    lambda m: not m.find_element(by, locator))
            except NoSuchElementException:
                pass

    def wait_for_element_displayed(self, by, locator, timeout=None):
        # TODO: Remove when we're using a version of Marionette with bug 957248 fixed
        timeout = timeout or (self.marionette.timeout and self.marionette.timeout / 1000.0) or 30
        Wait(self.marionette, timeout).until(
            lambda m: self.wait_for_element_present(by, locator).is_displayed())

    def wait_for_element_not_displayed(self, by, locator, timeout=None):
        if self.is_element_displayed(by, locator):
            # TODO: Remove when we're using a version of Marionette with bug 957248 fixed
            timeout = timeout or (self.marionette.timeout and self.marionette.timeout / 1000.0) or 30
            try:
                Wait(self.marionette, timeout).until(
                    lambda m: not self.wait_for_element_present(by, locator).is_displayed())
            except (NoSuchElementException, StaleElementException):
                pass

    def wait_for_condition(self, method, timeout=None):
        # TODO: Remove when we're using a version of Marionette with bug 957248 fixed
        timeout = timeout or (self.marionette.timeout and self.marionette.timeout / 1000.0) or 30
        Wait(self.marionette, timeout).until(method)

    def is_element_present(self, by, locator):
        self.marionette.set_search_timeout(0)
        try:
            self.marionette.find_element(by, locator)
            return True
        except NoSuchElementException:
            return False
        finally:
            self.marionette.set_search_timeout(self.marionette.timeout or 10000)

    def is_element_displayed(self, by, locator):
        self.marionette.set_search_timeout(0)
        try:
            return self.marionette.find_element(by, locator).is_displayed()
        except NoSuchElementException:
            return False
        finally:
            self.marionette.set_search_timeout(self.marionette.timeout or 10000)

    def select(self, match_string):
        # cheeky Select wrapper until Marionette has its own
        # due to the way B2G wraps the app's select box we match on text

        _list_item_locator = (By.XPATH, "id('value-selector-container')/descendant::li[descendant::span[.='%s']]" % match_string)
        _close_button_locator = (By.CSS_SELECTOR, 'button.value-option-confirm')

        # have to go back to top level to get the B2G select box wrapper
        self.marionette.switch_to_frame()

        self.wait_for_element_displayed(*_list_item_locator)
        li = self.marionette.find_element(*_list_item_locator)

       # TODO Remove scrollintoView upon resolution of bug 877651
        self.marionette.execute_script(
            'arguments[0].scrollIntoView(false);', [li])
        li.tap()

        close_button = self.marionette.find_element(*_close_button_locator)

        # Tap close and wait for it to hide
        close_button.tap()
        self.wait_for_element_not_displayed(*_close_button_locator)

        # now back to app
        self.apps.switch_to_displayed_app()

    @property
    def keyboard(self):
        from gaiatest.apps.keyboard.app import Keyboard
        return Keyboard(self.marionette)

    def wait_for_system_banner(self):
        """Waits for the system banner to appear and then disappear"""
        self.marionette.switch_to_frame()
        system_banner_locator = (By.ID, 'system-banner')
        self.wait_for_element_displayed(*system_banner_locator)
        self.wait_for_element_not_displayed(*system_banner_locator)
        self.apps.switch_to_displayed_app()


class PageRegion(Base):
    def __init__(self, marionette, element):
        self.root_element = element
        Base.__init__(self, marionette)
