# Copyright 2012 Robert Muth
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; version 3
# of the License.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.

"""
HocusPocus Plugin: chrome
"""


import logging
import tornado

import utils

CHROME = "/usr/bin/google-chrome"


def ChromeVersion():
    _, content = utils.RunCommand([CHROME, "--version"])
    return content


def ChromeOpenURL(url):
    _, content = utils.RunCommand([CHROME, "--new-window", url])
    return content


# noinspection PyAbstractClass
class Handler(tornado.web.RequestHandler):
    """Display the plugin page"""

    def initialize(self, template_args):
        logging.debug("chrome handler init")
        self._template_args = template_args

    def get(self, dummy_p, *dummy_k):
        logging.info("chrome handler request")
        self._template_args["version"] = ChromeVersion()
        print (self._template_args["version"])
        self.write(self.render_string("chrome.html", **self._template_args))
        self.finish()


# noinspection PyAbstractClass
class CommandHandler(tornado.web.RequestHandler):
    """Handle AJAXy requests"""

    def initialize(self, template_args):
        logging.debug("chrome command handler init")
        self._template_args = template_args

    def get(self, dummy_p, *dummy_k):
        command = self.get_argument("command")
        arg = self.get_argument("arg")

        logging.info("chrome command handler request [%s, %s]", command, arg)
        status = ""
        if command == "openurl":
            status = ChromeOpenURL(arg)
        self.write(status)
        self.finish()


def GetHandlers():
    return [(r"/chrome/(.*)", Handler),
            (r"/chrome_command(.*)", CommandHandler),
            ]


def GetTopics():
    return [r"chrome_command/#"]

def GetDependencies():
    return [CHROME]
