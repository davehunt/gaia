# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

from gaiatest.apps.base import Base


class Camera(Base):

    name = 'Camera'

    _progress_bar_locator = ('id', 'progress')
    _capture_button_locator = ('id', 'capture-button')
    _capture_button_enabled_locator = ('css selector', '#capture-button:not([disabled])')
    _focus_ring_locator = ('id', 'focus-ring')
    _film_strip_image_locator = ('css selector', '#filmstrip > img.thumbnail')
    _switch_source_button_locator = ('id', 'switch-button')
    _switch_to_gallery_button_locator = ('id', 'gallery-button')
    _video_capturing_locator = ('css selector', 'body.capturing')
    _video_timer_locator = ('id', 'video-timer')

    def launch(self):
        Base.launch(self)
        self.wait_for_element_not_displayed(*self._progress_bar_locator)

    def wait_for_capture_button_enabled(self):
        self.wait_for_element_present(*self._capture_button_enabled_locator)

    def tap_capture_button(self):
        self.wait_for_capture_button_enabled()
        capture_button = self.marionette.find_element(*self._capture_button_locator)
        capture_button.tap()

    def capture_photo(self):
        self.tap_capture_button()
        # Wait for focus ring to appear
        self.wait_for_element_displayed(*self._focus_ring_locator)

    def is_filmstrip_image_displayed(self):
        # Wait for filmstrip
        self.wait_for_element_displayed(*self._film_strip_image_locator)
        return self.marionette.find_element(*self._film_strip_image_locator).is_displayed()

    def tap_switch_source_button(self):
        switch_source_button = self.marionette.find_element(*self._switch_source_button_locator)
        switch_source_button.tap()

    def record_video(self, duration):
        # Start recording
        self.tap_capture_button()
        self.wait_for_element_present(*self._video_capturing_locator)
        # Wait for duration
        timer_text = "00:%02d" % duration
        self.wait_for_condition(lambda m: m.find_element(
            *self._video_timer_locator).text == timer_text, timeout=duration + 30)
        # Stop recording
        self.tap_capture_button()
        self.wait_for_element_not_displayed(*self._video_timer_locator)

    def switch_to_gallery(self):
        switch_to_gallery_button = self.marionette.find_element(*self._switch_to_gallery_button_locator)
        #self.marionette.tap(switch_to_gallery_button)
        switch_to_gallery_button.tap()
        from gaiatest.apps.gallery.app import Gallery
        gallery_app = Gallery(self.marionette)
        gallery_app.launch()
        return gallery_app
