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
        self.usersession = None

    def get_current_user(self):
        return self.get_secure_cookie("user")

    def get_current_session(self, sessionstring=None):
        if not sessionstring:
            sessionstring = self.get_secure_cookie("session")
        sessionhash = self.hash_string(sessionstring)
        self.usersession = Session(self.dbi, sessionhash)
        return self.usersession

    def hash_string(self, string):
        hasher = sha1(string)
        return hasher.hexdigest()

    def handle_authentication(self):
        if not self.current_user:
            self.redirect("/login")
            return
        try:
            self.usersession = self.get_current_session()
        except SessionTimeout:
            self.redirect("/login")
            return


class LoginHandler(BaseHandler):
    def get(self):
        self.render("login_form.html")

    def post(self):
        user = self.get_argument("user").strip()
        password = self.get_argument("pw").strip()
        passwordhash = self.hash_string(password)
        self.dbi.execute(
                "SELECT pwhash FROM users WHERE username=?",
                (user,))
        response = self.dbi.fetchone()
        if response is None:
            self.write({"message": "Incorrect."})
            self.redirect("/login")
            return
        true_passwordhash = response[0]
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
        backendformfile = "backend_form.html"
        self.dbi.execute("SELECT name FROM sqlite_master;")
        tablenames = map(lambda x: x[0], self.dbi.fetchall())
        self.render(backendformfile, tables=tablenames)

    def post(self):
        self.handle_authentication()
        backendformeditorfile = "backend_form_editor.html"
        table = self.get_argument("table")
        response = {"table": table}
        self.dbi.execute(
                "PRAGMA TABLE_INFO({0});".format(table))
        tableschema = [(x[1], x[2]) for x in self.dbi.fetchall()]

        self.dbi.execute("SELECT rowid,* FROM {0};".format(table))
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
            self.usersession.logout()
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


define("port", default=8889, help="run on the given port", type=int)
options.logging = "warning"
settings = {
            "static_path": os.path.join(os.path.dirname(__file__), "static"),
            #it is important, that you generate some proper randomness on your own.
            "cookie_secret": "Nzk4MmYwZmUzZTBmYmUwMDFjODcyNzM0Mzg0ZDc1ZWQgIC0K",
            "template_path": os.path.join(os.path.dirname(__file__), "static/templates")}

urls = [
        (r"/login", LoginHandler),
        (r"/", BackendHandler),
        (r"/backend", BackendHandler),
        (r"/customsql", CustomSQLHandler)
        ]

if __name__ == "__main__":
    tornado.options.parse_command_line()
    application = tornado.web.Application(urls, **settings)
    http_server = tornado.httpserver.HTTPServer(application)
    http_server.listen(options.port)
    tornado.ioloop.IOLoop.instance().start()
