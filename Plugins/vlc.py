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
HocusPocus Plugin "vlc" (video lan client)
"""

import logging

import tornado.web

import vlc_driver

# noinspection PyAbstractClass
class Handler(tornado.web.RequestHandler):
    """Handles the display of the vlc plugin page
    """

    def initialize(self, template_args):
        logging.debug("vlc handler init")
        self._template_args = template_args

    def get(self, dummy_p, *dummy_k):
        logging.info("vlc handler request")
        self.write(self.render_string("vlc.html", **self._template_args))
        self.finish()

# noinspection PyAbstractClass
class CommandHandler(tornado.web.RequestHandler):
    """Handles ajax request made by the vlc plugin page
    """

    def initialize(self, template_args):
        logging.debug("vlc command handler init")
        self._template_args = template_args

    def get(self, dummy_p, *dummy_k):
        command = self.get_argument("command")
        arg = self.get_argument("arg", None)
        logging.info("vlc command handler request [%s] [%s]", command, arg)

        status = vlc_driver.VlcRunCommand(command, arg)
        if status:
            status = "\n".join(status)
        else:
            status = "VLC does not appear to be running"
        self.write(status)
        self.finish()


def GetHandlers():
    return [(r"/vlc/(.*)", Handler),
            (r"/vlc_command(.*)", CommandHandler),
            ]


def GetTopics():
    return [r"/vlc_command/#"]


def GetDependencies():
    return vlc_driver.GetDependencies()
