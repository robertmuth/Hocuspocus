#!/usr/bin/python3
#
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
Main hocuspocus script
"""

# python includes
import importlib
import logging
import multiprocessing
import os
import sys

import tornado.autoreload
import tornado.ioloop
import tornado.options
import tornado.template
import tornado.web

VERSION = "3.0"

# ======================================================================

tornado.options.define("port",
                       default=8888,
                       type=int,
                       help="server port")

tornado.options.define("tasks",
                       default=4,
                       type=int,
                       help="size of task pool")

tornado.options.define("name",
                       default="no-name",
                       type=str,
                       help="name/purpose of this machine")

tornado.options.define("css_style_file",
                       default="static/hocuspocus.css",
                       type=str,
                       help="style file path")

tornado.options.define("config",
                       default="hocuspocus.conf",
                       type=str,
                       help="config file to read")

tornado.options.define("mqtt_broker",
                       default="",
                       type=str,
                       help="address of the mqtt broken")

OPTIONS = tornado.options.options


tornado.options.define(
    "plugins",
    default="",
    type=str,
    multiple=True,
    help="plugins")
# ======================================================================

# noinspection PyAbstractClass


class MainHandler(tornado.web.RequestHandler):
    """ Handler for root path - simply redirects to /about
    """

    def initialize(self, template_args):
        logging.debug("main handler init")

    def get(self):
        self.redirect("/about/")


# These args are passed to all
def GetBaseTemplateArgs(plugins):
    global OPTIONS
    return {
        "service_name": OPTIONS.name,
        "version": VERSION,
        "plugins": [{"name": name,
                     "url": name + "/"}
                    for name, _ in plugins if not name.startswith("@")],
        "css_style_file": OPTIONS.css_style_file,
    }


def _IsActive(mod):
    bad = 0
    for d in mod.GetDependencies():
        if not os.path.exists(d):
            logging.error(
                "dependency [%s] does not exist, plugin may not work properly", d)
            bad += 1
    return bad == 0


def _LoadPlugins():
    global OPTIONS
    modules = []
    for name in OPTIONS.plugins:
        fn = name[1:] if name.startswith("@") else name
        mod = importlib.import_module("Plugins." + fn, package="Plugins")
        if _IsActive(mod):
            logging.info("registering: %s", name)
            modules.append((name, mod))
    return modules


def _GetHandlers(plugins):
    handlers = [("/",
                 MainHandler,
                 # this is passed to the initialize() handler function
                 {"template_args": GetBaseTemplateArgs(plugins)})]

    for name, mod in plugins:
        template_args = GetBaseTemplateArgs(plugins)
        template_args["plugin_name"] = name[1:] if name.startswith(
            "@") else name
        template_args["plugin_extra"] = ""
        logging.info("preparing plugin: %s", name)

        for path, handler in mod.GetHandlers():
            # websockets are currently not used
            if "websocket" in path:
                handlers.append((path, handler))
            else:
                handlers.append(
                    (path, handler, {"template_args": template_args}))
    return handlers


def StartMqttListener(handlers):
    assert False


def main():
    # Trigger reload when we change some crucial files
    # which are not known to the automatic
    tornado.autoreload.watch("hocuspocus.conf")

    # first argument pass to determine the plugins
    tornado.options.parse_command_line()

    tornado.options.parse_config_file(OPTIONS.config)

    plugins = _LoadPlugins()
    for p in plugins:
        assert p[1].GetTopics
    # Another pass  because now more plugin options are known.
    tornado.options.parse_config_file(OPTIONS.config)

    handlers = _GetHandlers(plugins)

    logging.info("Installing Handlers:")
    for h in handlers:
        logging.info("%s: %s", h[0], h[1])

    if OPTIONS.mqtt_broker:
        StartMqttListener(handlers)

    application = tornado.web.Application(
        handlers,
        debug=True,
        task_pool=multiprocessing.Pool(OPTIONS.tasks),
        template_path="Templates/",
        static_path="Static/")

    logging.info("listening on port %d", OPTIONS.port)
    application.listen(OPTIONS.port)
    tornado.ioloop.IOLoop.instance().start()
    return 0


if __name__ == "__main__":
    sys.exit(main())
