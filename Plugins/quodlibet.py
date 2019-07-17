# Copyright (C)  2012 and onwards Robert Muth <robert at muth dot org>
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
HocusPocus Plugin "quodlibet"
"""

import json
import logging
import os

import tornado.web

import utils

QTOOL = "/usr/bin/quodlibet"

COMMANDS = {
    "play": [QTOOL, "--play"],
    "pause": [QTOOL, "--pause"],
    "next": [QTOOL, "--next"],
    "prev": [QTOOL, "--previous"],
    "fwd+": [QTOOL, "--seek=+00:01"],
    "ffwd": [QTOOL, "--seek=+00:10"],
    "fffwd": [QTOOL, "--seek=+01:40"],
    "rev": [QTOOL, "--seek=-00:01"],
    "rrev": [QTOOL, "--seek=-00:10"],
    "rrrev": [QTOOL, "--seek=-01:40"],

    "curr_song": [QTOOL, "--print-playing"],
    "status": [QTOOL, "--status"],
    "kill": [QTOOL, "--quit"],
}


def RunCommand(name, value=None, length=None):
    if name in COMMANDS:
        return utils.RunCommand(COMMANDS[name])
    elif name == "change_volume":
        return utils.RunCommand([QTOOL, "--volume=%d" % int(value)])
    elif name == "change_position":
        secs = int(length * int(value) / 100)
        time = "%d:%d" % (secs / 60, secs % 60)
        print(length, value, time)
        return utils.RunCommand([QTOOL, "--seek=%s" % time])
    else:
        logging.error("unknown command %s", name)
        return None, None


# >cat ~/.quodlibet/current
#  album=The Zzz
#  replaygain_reference_loudness=88.0 dB
#  replaygain_album_gain=-7.3 dB
#  ~#playcount=0
#  ~#bitrate=0
#  artist=Xxx
#  ~#length=254
#  title=Aaa
#  ~#rating=0.000000
#  replaygain_track_peak=0.99996
#  ~#lastplayed=0
#  ~#added=1330690593
#  replaygain_track_gain=-7.5 dB
#  ~filename=/music/zzz/track06.flac
#  ~#mtime=1328370622.4
#  tracknumber=6
#  ~mountpoint=/music
#  ~#laststarted=0
#  ~#skipcount=0
#  replaygain_album_peak=0.99996
#  ~format=FLAC

def GetCurrentSong():
    try:
        return open(os.getenv("HOME") + "/.quodlibet/current")
    except Exception as err:
        logging.error(str(err))
        return None


# >quodlibet  --status
#  playing SearchBar 0.579 inorder on 0.019
#  coltrane


def GetStatus():
    result = {
        "play_mode": "",
        "view": "no view",
        "volume": "0",
        "order": "",
        "repeat": "no",
        "position": "0",
        "stitle": "",
        "album": "",
        "artist": "",
        "rating": "0",
        "length": "0",
    }

    _, content = RunCommand("status")
    tokens = content.split()
    if len(tokens) >= 6:
        result["play_mode"] = tokens[0]
        result["view"] = tokens[1]
        result["volume"] = tokens[2]
        result["order"] = tokens[3]
        result["repeat"] = tokens[4]
        result["position"] = tokens[5]

    fp = GetCurrentSong()
    if fp:
        d = {}
        for line in fp:
            line = line.strip()
            key, val = line.split("=", 1)
            d[key] = val
        fp.close()
        result["artist"] = d.get("artist", "")
        result["title"] = d.get("title", "")
        result["album"] = d.get("album", "")
        result["rating"] = d.get("~#rating", "0")
        result["length"] = d.get("~#length", "0")
    else:
        result["title"] = "quodlibet appears to not be running"

    return result


# noinspection PyAbstractClass
class Handler(tornado.web.RequestHandler):
    """ Display quodlibet page
    """

    def initialize(self, template_args):
        logging.debug("quodlibet handler init")
        self._template_args = template_args

    def get(self, dummy_p, *dummy_k):
        logging.info("vlc handler request")
        self.write(self.render_string("quodlibet.html", **self._template_args))
        self.finish()


# noinspection PyAbstractClass
class CommandHandler(tornado.web.RequestHandler):
    """ AJAXy command handler
    """

    def initialize(self, template_args):
        logging.debug("vlc command handler init")
        self._template_args = template_args

    # TODO: fix this
    last_song_length = 0

    def get(self, dummy_p, *dummy_k):
        command = self.get_argument("command")
        value = self.get_argument("value")
        logging.info("quodlibet command handler request [%s]", command)
        if command != "status":
            _, _ = RunCommand(command, value, CommandHandler.last_song_length)
        else:
            d = GetStatus()
            CommandHandler.last_song_length = float(d.get("length"))
            self.write(json.dumps(d))

        self.finish()


def GetHandlers():
    return [(r"/quodlibet/(.*)", Handler),
            (r"/quodlibet_command(.*)", CommandHandler),
            ]


def GetTopics():
    return [r"/quodlibet_command/#"]


def GetDependencies():
    return [QTOOL]
