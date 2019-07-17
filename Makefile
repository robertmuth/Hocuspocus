# Hocuspocus Makefile
#
# Copyright (C) 2012 Robert Muth
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, version 3 of the License.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
#
# Note, since Hocuspocus is written entirely in python, no real
# build step is necessary. However, you like will need to run
#    make install_tornado
#

#@ Available Targets:
#@
 
#@ Help - Show this messsage
#@
help:
	@egrep "^#@" ${MAKEFILE_LIST} | cut -c 3-

#@ html_check
#@
html_check:
	tidy -xml index.html >/dev/null

#@ code_check
#@
code_check:
	pylint  --rcfile=pylintrc  *.py Plugins/*.py

#@ clean
#@
clean:
	$(RM) *.confc *.pyc *.pyo *.log Plugins/*pyc Plugins/*pyo

#@ tar
#@
tar: clean
	cd ..;tar cfz hocuspocus.$(VERSION).tar.gz  Hocuspocus


