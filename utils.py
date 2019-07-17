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
HocusPocus utils
"""

import logging
import os
import subprocess


class Datablob:
    def __init__(self, **args):
        self.__dict__.update(args)

    def __str__(self):
        return str(self.__dict__)


def FileStem(filename):
    if filename.endswith("/"):
        filename = filename[:-1]
    filename = os.path.split(filename)[1]
    base = os.path.splitext(filename)[0]
    base = base.replace("-", "_-_")
    base = base.replace("_", " ")
    base = base.replace(".", " ")
    return base


def MakeHtmlBulletsEmpty(n):
    return "&#9675;" * n


def MakeHtmlBulletsFull(n):
    return "&#9679;" * n


def MakeHtmlSquaresEmpty(n):
    return "&#9633;" * n


def MakeHtmlSquaresFull(n):
    return "&#9632;" * n


def EscapeContents(contents):
    contents = contents.replace("&", "&amp;")
    contents = contents.replace("<", "&lt;")
    contents = contents.replace(">", "&gt;")
    return contents


def RunCommand(cmd, inp=None, stderr_mode=subprocess.STDOUT):
    """Returns
    """
    try:
        process = subprocess.Popen(cmd,
                                   close_fds=True,
                                   stdin=subprocess.PIPE,
                                   stderr=stderr_mode,
                                   stdout=subprocess.PIPE)
        logging.info("running pid %d [%s] [%s]", process.pid, cmd, repr(inp))
        logging.info(" ".join(cmd))
        if inp is not None:
            process.stdin.write(bytes(inp, "utf-8"))
            process.stdin.close()
        data = process.stdout.read()
        process.wait()
        logging.info("complete")
        return process.returncode, str(data, "utf-8")
    except Exception as err:
        logging.error("command failed: " + str(err))
        return -1, str(err)


def RunCommandBackground(cmd):
    process = subprocess.Popen(cmd,
                               close_fds=True)
    logging.info("running pid background %d [%s]", process.pid, cmd)
    return
