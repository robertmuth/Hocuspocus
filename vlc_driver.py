# Copyright 2011 Robert Muth
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
HocusPocus vlc utilities
"""

# python imports
import logging
import os
import socket

# local imports
import utils

# note this assumes vlc was started like with:
# "-extraintf=rc --rc-host=localhost:23232"
#
# For manual experiments, simply run:
# telnet localhost 23232
# and use the command line interface

# https://wiki.videolan.org/Documentation:Modules/telnet/
# https://wiki.videolan.org/Talk:Console/

VLC = "/usr/bin/vlc"
VLC_LAUNCH_CMD = [VLC,
                 "--one-instance",
                 "--rc-fake",
                 "--extraintf=rc",
                 "--rc-host=localhost:23232"]

VLC_PLAY_AND_EXIT_CMD = [VLC, "--play-and-exit"]


KILLALL = "/usr/bin/killall"

VLC_KILL_CMD = [KILLALL,
                "-9",
                "vlc"]

if not os.path.exists(VLC):
    logging.fatal("missing binary %s", VLC)


VLC_SERVER = ("", 23232)


def ReadSocketToPrompt(s):
    res = ""
    while 1:
        res += str(s.recv(1024), "utf-8")
        if res.endswith("\r\n> "):
            return res


def VlcRunRawCommand(comm, arg):

    logging.info("vlc command is [%s] [%s]", repr(comm), repr(arg))
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        s.connect(VLC_SERVER)
        s.settimeout(0.2)
        ReadSocketToPrompt(s)
    except Exception as err:
        logging.error(str(err))
        return None

    if arg:
        comm += " " + arg
    s.send(bytes(comm + "\n", "utf-8"))
    res = ""
    while 1:
        try:
            res += str(s.recv(1024), "utf-8")
        except Exception as err:
            logging.error(repr(err))
            break
    s.close()
    res = res.split("\r\n")
    return res


def VlcIsRunning():
    try:
        res = VlcRunCommand("status")
        return res
    except Exception as err:
        logging.error(str(err))
        return None


def VlcLaunch(media=None):
    logging.info("launch vlc [%s]", media)
    if media:
        utils.RunCommandBackground(VLC_LAUNCH_CMD + [media])
    else:
        utils.RunCommandBackground(VLC_LAUNCH_CMD)


def VlcPlayAndExit(media):
    logging.info("start vlc [%s]", media)
    utils.RunCommandBackground(VLC_PLAY_AND_EXIT_CMD + [media])

def VlcAdd(media):
    logging.info("add vlc [%s]", media)
    VlcRunRawCommand("add %s\n" % media)


def VlcRelativeSeek(n):
    result = VlcRunCommand("get_time")
    # print(repr(result))
    result = int(result[0]) + int(n)
    logging.info("seek vlc [%d]", result)
    VlcRunRawCommand("seek %d\n" % result)


def VlcPlay(media):
    if VlcIsRunning():
        VlcRunCommand("clear")
        VlcAdd(media)
    else:
        VlcLaunch(media)


def VlcKill():
    logging.info("kill vlc")
    utils.RunCommand(VLC_KILL_CMD)


SPECIAL_VLC_COMMANDS = {
    "launch": VlcLaunch,
    "play_and_exit": VlcPlayAndExit,
    "seek_rel": VlcRelativeSeek,
    "kill": VlcKill,
}

VLC_ALLOWED_COMMANDS = {
    "fullscreen",

    "volup",
    "voldown",

    "faster",
    "slower",


    "chapter",
    "play",
    "stop",
    "pause",

    "title_n",
    "title_p",
    "chapter_n",
    "chapter_p",
    "next",
    "prev",

    "clear",

    "get_time",

    "status",

    #"add": "add %s",
}


def VlcRunCommand(command, arg):
    logging.info("command %s %s", command, arg)
    if command in VLC_ALLOWED_COMMANDS:
        return VlcRunRawCommand(command, arg)
    elif command in SPECIAL_VLC_COMMANDS:
        val = SPECIAL_VLC_COMMANDS[command]
        return val(arg)
    else:
        logging.error("unknown command")


def GetDependencies():
    return [KILLALL, VLC]
