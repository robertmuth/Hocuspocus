# Copyright 2012 and onwards Robert Muth <robert at muth dot org>
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
HocusPocus Plugin "system"

This is a plugin for running short non-interactive jobs
"""

import logging

import tornado

import utils

# ======================================================================

tornado.options.define(
    "system_commands",
    default="",
    type=str,
    multiple=True,
    help="TODO")

tornado.options.define(
    "system_queries",
    default="",
    type=str,
    multiple=True,
    help="TODO")

OPTIONS = tornado.options.options


# ======================================================================
def GetQueries():
    names = []
    for s in OPTIONS.system_queries:
        tokens = s.split(":")
        names.append(tokens[0])
    return names


def RunQuery(name):
    for s in OPTIONS.system_queries:
        tokens = s.split(":")
        if name == tokens[0]:
            return utils.RunCommand(tokens[1].split())

    logging.error("unknown query %s", name)
    return None, None


def GetCommands():
    names = []
    for s in OPTIONS.system_commands:
        tokens = s.split(":")
        names.append(tokens[0])
    return names


def RunCommand(name):
    for s in OPTIONS.system_commands:
        tokens = s.split(":")
        if name == tokens[0]:
            return utils.RunCommand(tokens[1].split())

    logging.error("unknown command %s", name)
    return None, None


class Handler(tornado.web.RequestHandler):
    """ Display page listing and available commands """

    def initialize(self, template_args):
        logging.debug("system handler init")
        self._template_args = template_args

    def get(self, dummy_p, *dummy_k):
        logging.info("system handler request")
        self._template_args["status"] = ""
        self._template_args["queries"] = GetQueries()
        self._template_args["commands"] = GetCommands()
        self.write(self.render_string("system.html", **self._template_args))
        self.finish()


# noinspection PyAbstractClass
class CommandHandler(tornado.web.RequestHandler):
    """ AJAXy commanbd handler """

    def initialize(self, template_args):
        logging.debug("system command handler init")
        self._template_args = template_args

    def get(self, dummy_p, *dummy_k):
        command = self.get_argument("command")
        logging.info("system command handler request [%s]", command)
        _, content = RunCommand(command)
        self.write(content)
        self.finish()


# noinspection PyAbstractClass
class QueryHandler(tornado.web.RequestHandler):
    """ AJAXy commanbd handler """

    def initialize(self, template_args):
        logging.debug("system query handler init")
        self._template_args = template_args

    def get(self, dummy_p, *dummy_k):
        query = self.get_argument("query")
        logging.info("system query handler request [%s]", query)
        _, content = RunQuery(query)
        self.write(content)
        self.finish()


def GetHandlers():
    return [(r"/system/(.*)", Handler),
            (r"/system_query(.*)", QueryHandler),
            (r"/system_command(.*)", CommandHandler),
            ]


def GetTopics():
    return [r"/system_command/#"]


def GetDependencies():
    return []
