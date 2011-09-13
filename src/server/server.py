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
import string
import os
from cgi import escape as html_escape
import random
from modules.Sessions import Session, SessionTimeout
from modules.DBInterface import DBInterface
from hashlib import sha1
import tornado.httpserver
import tornado.ioloop
import tornado.options
import tornado.web
from tornado.options import define, options

DATABASEFILE = "database.db"

__author__ = "Barthimaeus"
__email__ = "barthimaeus@web.de"


class BaseHandler(tornado.web.RequestHandler):
    def __init__(self, var1, var2):
        super(BaseHandler, self).__init__(var1, var2)
        self.dbi = DBInterface("database.db")

    def get_current_user(self):
        return self.get_secure_cookie("user")

    def get_current_session(self, sessionstring=None):
        if not sessionstring:
            sessionstring = self.get_secure_cookie("session")
        sessionhash = self.hash_string(sessionstring)
        usersession = Session(self.dbi, sessionhash)
        return usersession

    def hash_string(self, string):
        hasher = sha1(string)
        return hasher.hexdigest()

    def handle_authentication(self):
        if not self.current_user:
            self.redirect("/login")
            return
        try:
            usersession = self.get_current_session()
        except SessionTimeout:
            self.redirect("/login")
            return


class LoginHandler(BaseHandler):
    def get(self):
        loginfile = open("static/templates/login_form.html", "r")
        self.write(loginfile.read())

    def post(self):
        user = self.get_argument("user").strip()
        password = self.get_argument("pw").strip()
        passwordhash = self.hash_string(password)
        self.dbi.execute(
                "SELECT pwhash FROM users WHERE username=?",
                (user,))
        true_passwordhash = self.dbi.fetchone()[0]
        if passwordhash == true_passwordhash:
            sessionstring = ""
            for x in range(20):
                characterset = string.join(
                                    string.ascii_uppercase,
                                    string.digits)
                sessionstring += random.choice(characterset)
            self.set_secure_cookie("user", self.get_argument("user"))
            self.set_secure_cookie("session", sessionstring)
            usersession = self.get_current_session(sessionstring)
            self.write({"message": "Accepted."})
        else:
            self.write({"message": "Incorrect."})
            self.redirect("/login")


class BackendHandler(BaseHandler):
    def get(self):
        self.handle_authentication()
        backendformfile = "static/templates/backend_form.html"
        self.dbi.execute("SELECT name FROM sqlite_master;")
        tablenames = map(lambda x: x[0], self.dbi.fetchall())
        self.render(backendformfile, tables=tablenames)

    def post(self):
        self.handle_authentication()
        backendformeditorfile = "static/templates/backend_form_editor.html"
        table = self.get_argument("table")
        response = {"table": table}
        self.dbi.execute(
                "SELECT sql FROM sqlite_master WHERE name=?;",
                (table,))
        tablestatement = self.dbi.fetchone()[0]
        tablestatement = tablestatement.split("(")
        tablestatement = "".join(tablestatement[1:])
        tablestatement = tablestatement.split(")")
        tablestatement = "".join(tablestatement[:-1])
        tablestatement = tablestatement.split(", ")
        mapfunc = (lambda x:
                        (not ((" REFERENCES " in x) or (" references " in x))
                         and x
                         or x.split(" ")[0]))
        tableschema = map(mapfunc, tablestatement)

        self.dbi.execute("SELECT * FROM {0};".format(table))
        tablerows = self.dbi.fetchall()
        escapefunction = lambda x: html_escape("%s" % x)
        tablerows = [map(escapefunction, x) for x in tablerows]

        renderedtemplate = self.render_string(
                                backendformeditorfile,
                                schema=tableschema,
                                rows=tablerows,
                                table=table)
        response["table"] = table
        response["editortemplate"] = renderedtemplate
        self.write(response)


class CustomSQLHandler(BaseHandler):
    def post(self):
        self.handle_authentication()
        query = self.get_argument("sqlinput")
        if query == "logout":
            usersession.logout()
            self.write({"status": "ok", "response": "logged out"})
            self.finish()
            return
        response = {}
        try:
            self.dbi.execute(query)
            response["status"] = "ok"
            response["response"] = self.dbi.fetchall()
            self.dbi.commit()
        except sqlite3.Error, e:
            response["status"] = "ok"
            response["response"] = repr(e)
            self.dbi.commit()
        self.write(response)


define("port", default=8888, help="run on the given port", type=int)
settings = {
            "static_path": os.path.join(os.path.dirname(__file__), "static"),
            #it is important, that you generate some proper randomness on your own.
            "cookie_secret": "Nzk4MmYwZmUzZTBmYmUwMDFjODcyNzM0Mzg0ZDc1ZWQgIC0K"
            }

urls = [
        (r"/login", LoginHandler),
        (r"/backend", BackendHandler),
        (r"/customsql", CustomSQLHandler)
        ]

if __name__ == "__main__":
    tornado.options.parse_command_line()
    application = tornado.web.Application(urls, **settings)
    http_server = tornado.httpserver.HTTPServer(application)
    http_server.listen(options.port)
    tornado.ioloop.IOLoop.instance().start()
