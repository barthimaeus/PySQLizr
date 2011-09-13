# Copyright 2011, Barthimaeus <barthimaeus@web.de>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import sqlite3

class DBInterface(object):
    def __init__(self, file):
        self.database = sqlite3.connect(file)
        self.curs = self.database.cursor()
        self.execute = self.curs.execute
        self.fetchone = self.curs.fetchone
        self.fetchall = self.curs.fetchall
        self.commit = self.database.commit
        self.execute("pragma foreign_keys=on;")

    def table_exists(self, name):
        self.execute("SELECT name FROM sqlite_master WHERE name=?", (name,))
        return self.fetchone() and True