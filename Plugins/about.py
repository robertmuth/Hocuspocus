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
HocusPocus Plugin "about"
"""

import logging

import tornado.web


# noinspection PyAbstractClass
class Handler(tornado.web.RequestHandler):

    def initialize(self, template_args):
        logging.debug("about handler init")
        self._template_args = template_args

    def get(self, dummy_p, *dummy_k):
        logging.info("about handler request")
        self.write(self.render_string("about.html", **self._template_args))
        self.finish()


def GetHandlers():
    return [(r"/about/(.*)", Handler),
            ]


def GetTopics():
    return []


def GetDependencies():
    return []
