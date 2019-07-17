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
HocusPocus Plugin "media"
"""

import glob
import json
import logging
import os
import stat
import time

import tornado

import utils
import vlc_driver

# ======================================================================

tornado.options.define(
    "media_contents",
    default="",
    type=str,
    multiple=True,
    help="media_plugin: content")

OPTIONS = tornado.options.options


# ======================================================================


def getmtime(filename):
    return os.stat(filename)[stat.ST_MTIME]


def GetMostRecent(max_age, patterns):
    now = time.time()
    media = []
    for p in patterns:
        media += glob.glob(p)
    lst = [(getmtime(a), a) for a in media if now < getmtime(a) + max_age]
    lst.sort()
    lst.reverse()
    return [[utils.FileStem(b), b] for a, b in lst]


def GlobListAndSort(patterns):
    files = []
    for f in patterns:
        files += glob.glob(f)
    files.sort()
    return [[utils.FileStem(x), x] for x in files]


def GetMediaFromFile(filename):
    try:
        data = open(filename).read()
    except Exception as err:
        logging.error(str(err))
        data = ""

    result = []
    for line in data.split("\n"):
        if not line or line.startswith("#"):
            continue
        try:
            loc, name = line.split(None, 1)
            result.append([name, loc])
        except Exception as err:
            logging.error("bad line: %s", line)
    return result


# ======================================================================
# Exported Interface
# ======================================================================

def GetGenres():
    """Return a list of strings"""
    genres = []
    for content in OPTIONS.media_contents:
        tokens = content.split(":")
        genres.append(tokens[0])

    return genres


def GetMediaForGenre(genre):
    """Return a list of typles (name, file)"""
    for content in OPTIONS.media_contents:
        tokens = content.split(":")
        if tokens[0] != genre:
            continue
        if tokens[1] == "GlobListAndSort":
            return GlobListAndSort(tokens[2:])
        elif tokens[1] == "GetMediaFromFile":
            return GetMediaFromFile(tokens[2])
        elif tokens[1] == "GetMostRecent":
            return GetMostRecent(int(tokens[2]), tokens[3:])
        elif tokens[1] == "GetVerbatim":
            return [[tokens[2], tokens[3]]]
        else:
            logging.error("unknown genre [%s]", genre)
            return []


######################################################################

# noinspection PyAbstractClass
class HandlerMedia(tornado.web.RequestHandler):
    """ Display page listing and the genres """

    def initialize(self, template_args):
        logging.debug("media handler init")
        self._template_args = template_args

    def get(self, *dummy_k):
        logging.info("media handler request")
        self.write(self.render_string("media.html", **self._template_args))
        self.finish()


# noinspection PyAbstractClass
class HandlerGenre(tornado.web.RequestHandler):
    """ Display page with all contents for a give genre"""

    def initialize(self, template_args):
        logging.debug("genre handler init")
        self._template_args = template_args

    def get(self, dummy_p, *dummy_k):
        self.write(self.render_string("genre.html", **self._template_args))
        self.finish()


# noinspection PyAbstractClass
class HandlerMediaListGenres(tornado.web.RequestHandler):
    """ Display page with all contents for a give genre"""

    def initialize(self, template_args):
        logging.debug("genre handler init")
        self._template_args = template_args

    def get(self, *dummy_k):
        self.write(json.dumps(GetGenres()))
        self.finish()


# noinspection PyAbstractClass
class HandlerMediaListMedia(tornado.web.RequestHandler):
    """ Display page with all contents for a give genre"""

    def initialize(self, template_args):
        logging.debug("genre handler init")
        self._template_args = template_args

    def get(self, *dummy_k):
        genre = self.get_argument("genre")
        self.write(json.dumps(GetMediaForGenre(genre)))
        self.finish()


# noinspection PyAbstractClass
class HandlerPlayMedia(tornado.web.RequestHandler):
    """ AJAXy commanbd handler """

    def initialize(self, template_args):
        logging.debug("playmedia handler init")
        self._template_args = template_args

    def get(self, dummy_p, *dummy_k):
        item = self.get_argument("item")
        logging.info("playmedia handler request %s", item)
        vlc_driver.VlcPlay(item)
        self.finish()


def GetHandlers():
    return [(r"/media_list_genres", HandlerMediaListGenres),
            (r"/media_list_media", HandlerMediaListMedia),
            (r"/media/", HandlerMedia),
            (r"/genre(.*)", HandlerGenre),
            (r"/playmedia(.*)", HandlerPlayMedia),
            ]


def GetTopics():
    return []


def GetDependencies():
    return []
