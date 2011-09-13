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

from DBInterface import DBInterface
from time import time

class Session(object):
    def __init__(self, dbi, session):
        self.dbi = dbi
        query = ""
        if not self.dbi.table_exists("sessions"):
            self.dbi.execute(
                    """CREATE TABLE sessions
                    (id INTEGER PRIMARY KEY, session STRING,
                    timeout STRING);""")

        if not self.dbi.table_exists("sessionstore"):
            self.dbi.execute(
                    """CREATE TABLE sessionstore
                    (id INTEGER PRIMARY KEY, key STRING, value STRING,
                    session REFERENCES sessions(id));""")
        self.dbi.execute("SELECT timeout FROM sessions WHERE session=?;",
                         (session,))

        response = self.dbi.fetchone()
        if response is None:
            self.dbi.execute(
                    """INSERT INTO sessions
                    (session, timeout) VALUES (?,?);""",
                    (session,time()+60*60))
            self.dbi.commit()
        elif response[0] < time():
            raise SessionTimeout()
        self.dbi.execute("SELECT id FROM sessions WHERE session=?;",
                         (session,))
        self.session = self.dbi.fetchone()[0]
        self.cache = None

    def logout(self):
        self.dbi.execute("UPDATE sessions SET timeout=? WHERE id=?;",
                         ('0', self.session))
        self.dbi.commit()

    def __contains__(self, key):
        self.dbi.execute(
                    """SELECT value FROM sessionstore
                    WHERE session=? AND key=?;""",
                    (self.session, key))
        self.cache = self.dbi.fetchone()
        return self.cache and True or False

    def __setitem__(self, key, val):
        if key in self:
            self.dbi.execute(
                        """UPDATE sessionstore SET value=?
                        WHERE session=? AND key=?;""",
                        (val, self.session, key))
        else:
            self.dbi.execute(
                             """INSERT INTO sessionstore
                             (key, value, session) VALUES(?,?,?);""",
                             (key, val, self.session))
        self.dbi.commit()

    def __getitem__(self, key):
        if key in self:
            return self.cache[0]
        else:
            return None

    def __delitem__(self, key):
        if key in self:
            self.dbi.execute(
                        """DELETE FROM sessionstore WHERE key=?
                        AND session=?;""",
                        (key, self.session))




class SessionTimeout(Exception):
    def __init__(self):
        self.message = "Session timed out."

    def __repr__(self):
        return self.message


#Example
if __name__== "__main__":
    dbi = db_interface("test.db")
    r = Session(dbi, "robert")
    r["spam"] = "eggs"







