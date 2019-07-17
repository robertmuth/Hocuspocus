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
HocusPocus Plugin "webcam"
"""

# python imports
import glob
import logging
import os

import tornado.options
import tornado.web

# local imports
import utils

STREAMER = "/usr/bin/streamer"
COMMAND = STREAMER + " -q -c %s -s %s -o %s"

# ======================================================================

tornado.options.define(
    "webcam_devices",
    default="",
    type=str,
    multiple=True,
    help="webcam_devices: camera devices")

tornado.options.define(
    "webcam_resolution",
    default="320x240",
    type=str,
    help="webcam_resolution: camera capture resolution")

OPTIONS = tornado.options.options


# ======================================================================

class Camera:
    def __init__(self, device, description):
        self.no = device
        self.description = description
        self._device = device

    def GetPicture(self):
        pass


def GetCameras():
    result = []
    for cam in OPTIONS.webcam_devices:
        description, device = cam.split(":")
        if description == "@ALL@":
            for fn in glob.glob(device):
                result.append(Camera(fn, os.path.basename(fn)))
        else:
            result.append(Camera(device, description))
    return result


# noinspection PyAbstractClass
class Handler(tornado.web.RequestHandler):
    """ Display webcam page"""

    def initialize(self, template_args):
        logging.debug("webcam handler init")
        self._template_args = template_args

    def get(self, dummy_p, *dummy_k):
        logging.info("pulse handler request")
        cameras = GetCameras()

        self._template_args["cameras"] = cameras
        self.write(self.render_string("webcam.html", **self._template_args))
        self.finish()


def GetJpeg(camera):
    logging.info("GetJpeg  " + camera)
    filename = "/tmp/hocuspocus%s.jpeg" % camera.replace("/", "-")
    if os.path.exists(filename):
        os.remove(filename)
    cmd = COMMAND % (camera, OPTIONS.webcam_resolution, filename)
    _, _ = utils.RunCommand(cmd.split())
    logging.info("opening")
    try:
        with open(filename, "rb") as fp:
            logging.info("reading")
            data = fp.read()
        logging.info("GetJpeg completed %d", len(data))
        return data
    except Exception as err:
        logging.error("webcam issues: " + str(err))
        return None


# noinspection PyAbstractClass
class CommandHandler(tornado.web.RequestHandler):
    """ AJAXy request handler"""

    def initialize(self, template_args):
        logging.debug("webcam command handler init")
        self._template_args = template_args

    # explore use of:
    # http://www.tornadoweb.org/en/stable/gen.html
    def get(self, dummy_p, *dummy_k):
        command = self.get_argument("command")
        camera = self.get_argument("camera")
        logging.info("webcam command handler request [%s]", command)
        if command == "get_picture":
            data = GetJpeg(camera)
            logging.info("SendJpeg completed %d", len(data))
            self.set_header("Content-Type", "image/jpeg")
            self.set_header("Content-Length", len(data))
            self.write(data)
            self.finish()

        else:
            logging.error("unknown command [%s]", command)
            self.finish()


def GetHandlers():
    return [(r"/webcam/(.*)", Handler),
            (r"/webcam_command(.*)", CommandHandler),
            ]


def GetTopics():
    return []


def GetDependencies():
    return [STREAMER]
