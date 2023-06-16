from __future__ import annotations

import os
import shutil
import socket
import sys
import time
from http.client import CannotSendRequest

import stem.process
from selenium import webdriver
from selenium.common.exceptions import WebDriverException
from selenium.webdriver import DesiredCapabilities, firefox
from selenium.webdriver.firefox.firefox_binary import FirefoxBinary
from selenium.webdriver.remote.webdriver import WebDriver as RemoteWebDriver
from stem.control import Controller
from stem.util import term

from helper import log, utils

sys.path.append('../..')


class TorBrowserDriver(webdriver.Firefox, RemoteWebDriver):
    def __init__(self,  DISABLE_RANDOMIZEDPIPELINENING=False):
        self.is_running = False

        # Initialize Tor Browser's profile
        self.profile = webdriver.FirefoxProfile()

        # set homepage to a blank tab
        self.profile.set_preference('browser.startup.page', "0")
        self.profile.set_preference('browser.startup.homepage', 'about:newtab')

        if DISABLE_RANDOMIZEDPIPELINENING:
            self.profile.set_preference(
                'network.http.pipelining.max-optimistic-requests', 5000)
            self.profile.set_preference(
                'network.http.pipelining.maxrequests', 15000)
            self.profile.set_preference('network.http.pipelining', False)

        self.profile.set_preference(
            'extensions.torlauncher.prompt_at_startup',
            0)

        # Disable cache - Wang & Goldberg's setting
        self.profile.set_preference('network.http.use-cache', False)

        # http://www.w3.org/TR/webdriver/#page-load-strategies-1
        # wait for all frames to load and make sure there's no
        # outstanding http requests (except AJAX)
        # https://code.google.com/p/selenium/wiki/DesiredCapabilities
        self.profile.set_preference('webdriver.load.strategy', 'conservative')
        # Note that W3C doesn't mention "conservative", this may change in the
        # upcoming versions of the Firefox Webdriver
        # https://w3c.github.io/webdriver/webdriver-spec.html#the-page-load-strategy

        self.profile.set_preference('permissions.memory_only', False)
        self.profile.update_preferences()
        # Initialize Tor Browser's binary
        self.binary = FirefoxBinary()

        # Initialize capabilities
        self.mycapabilities = DesiredCapabilities.FIREFOX
        self.mycapabilities.update({'handlesAlerts': True,
                                    'databaseEnabled': True,
                                    'javascriptEnabled': True,
                                    'browserConnectionEnabled': True})

        try:
            super(TorBrowserDriver, self)\
                .__init__(firefox_profile=self.profile,
                          firefox_binary=self.binary,
                          capabilities=self.mycapabilities)
            # executable_path=utils.geckodrive_path)
            self.is_running = True
        except WebDriverException as error:
            log.wl_log.error("WebDriverException while connecting to Webdriver %s"
                             % error)
        except socket.error as skterr:
            log.wl_log.error("Error connecting to Webdriver", exc_info=True)
            log.wl_log.error(skterr.strerror)
        except Exception as e:
            log.wl_log.error("Error connecting to Webdriver: %s" % e,
                             exc_info=True)

    def quit(self, _timeout=600):
        """
        Overrides the base class method cleaning the timestamped profile.

        """
        utils.timeout(_timeout)
        self.is_running = False
        try:
            super(TorBrowserDriver, self).quit()
            utils.cancel_timeout()
        except CannotSendRequest:
            log.wl_log.error("CannotSendRequest while quitting TorBrowserDriver",
                             exc_info=False)
            # following is copied from webdriver.firefox.webdriver.quit() which
            # was interrupted due to an unhandled CannotSendRequest exception.

            # kill the browser
            self.binary.kill()
            # remove the profile folder
            try:
                shutil.rmtree(str(self.profile.path))
                if self.profile.tempfolder is not None:
                    shutil.rmtree(self.profile.tempfolder)
                utils.cancel_timeout()
            except Exception as e:
                print(str(e))
        except Exception:
            log.wl_log.error("Exception while quitting TorBrowserDriver",
                             exc_info=True)
            utils.cancel_timeout()


if __name__ == "__main__":
    print('test ok!')
