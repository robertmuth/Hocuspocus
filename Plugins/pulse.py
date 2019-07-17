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
HocusPocus Plugin "pulse" (pulse audio)
"""

import logging

import tornado

import utils

PACTL = "/usr/bin/pactl"


def _PulseCommand(s):
    logging.info("Pulse command: %s", s)
    return utils.RunCommand([PACTL] + s)


def _PulseStatus():
    return _PulseCommand(["stat"])


def _PulseList(kind):
    return _PulseCommand(["list", kind])


def _PulseReset():
    return _PulseCommand(["exit"])


def _ExtractVolume(s):
    tokens = s.split()
    for t in tokens:
        if t.endswith("%"):
            return t[:-1]


class Device:
    def __init__(self, no, lines, is_sink):
        assert no.startswith("#")
        no = no[1:]
        self.is_sink = is_sink
        self.description = "no_description"
        self.app_name = "no_name"
        self.volume = "no_volume"
        self.base_volume = "no_volume"
        self.mute = "no_mute"
        self.state = "no_state"
        self.steps = 0
        self.no = no
        self.active_port = ""
        for l in lines:
            l = l.strip()
            tokens = l.split(":", 1)
            if l.startswith("Volume:"):
                # NOTE: ignoring other stere channel
                self.volume = _ExtractVolume(l)
            elif l.startswith("Base Volume:"):
                self.base_volume = _ExtractVolume(l)
            elif l.startswith("Mute:"):
                self.mute = tokens[1]
            elif l.startswith("State:"):
                self.state = tokens[1]
            elif l.startswith("Description:"):
                self.description = tokens[1]
            elif l.startswith("Active Port:"):
                self.active_port = tokens[1]


def _GetDevices(kind, is_sink):
    devs = []
    _, out = _PulseList(kind)
    sections = out.split("\n\n")
    for s in sections:
        lines = s.split("\n")
        header = lines.pop(0)
        section_type, no = header.rsplit(None, 1)
        devs.append(Device(no, lines, is_sink))
    return devs


# noinspection PyAbstractClass
class Handler(tornado.web.RequestHandler):
    def initialize(self, template_args):
        logging.debug("pulse handler init")
        self._template_args = template_args
        status = _PulseStatus()[1]
        sinks = _GetDevices("sinks", True)
        inputs = _GetDevices("sources", False)
        self._template_args["status"] = status
        self._template_args["inputs"] = inputs
        self._template_args["sinks"] = sinks

    def get(self, dummy_p, *dummy_k):
        logging.info("pulse handler request")
        self.write(self.render_string("pulse.html", **self._template_args))
        self.finish()


# noinspection PyAbstractClass
class CommandHandler(tornado.web.RequestHandler):
    def initialize(self, template_args):
        logging.debug("pulse command handler init")
        self._template_args = template_args

    def get(self, dummy_p, *dummy_k):
        command = self.get_argument("command")
        device = self.get_argument("device")
        value = self.get_argument("value")
        logging.info("pulse command handler request [%s]", command)
        if command == "source_mute":
            _PulseCommand(["set-source-mute", device, value])
        elif command == "sink_mute":
            _PulseCommand(["set-sink-mute", device, value])
        elif command == "source_vol":
            _PulseCommand(["set-source-volume", device, "%d%%" % int(value)])

        elif command == "sink_vol":
            _PulseCommand(["set-sink-volume", device, "%d%%" % int(value)])
        else:
            logging.error("unknown command [%s]", command)
        self.finish()


def GetHandlers():
    return [(r"/pulse/(.*)", Handler),
            (r"/pulse_command(.*)", CommandHandler),
            ]


def GetTopics():
    return [r"/pulse_command/#"]


def GetDependencies():
    return [PACTL]
