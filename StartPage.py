# -*- coding: utf-8 -*-

import os
import webapp2
import jinja2

from google.appengine.api import users

jinja_environment = jinja2.Environment(
    loader = jinja2.FileSystemLoader(os.path.dirname(__file__)))

class StartPage(webapp2.RequestHandler):
  def get(self):
    user = users.get_current_user()
    if not user:    # user not logged in
        self.redirect("/login")
    else:
        self.redirect('/mycard/view')

class Login(webapp2.RequestHandler):
  def get(self):
    self.response.out.write(jinja_environment.get_template("templates/login.html").render(
        loginurl = users.create_login_url("/mycard/view")
    ))

app = webapp2.WSGIApplication([
  ('/', StartPage),
  ('/login', Login),
], debug=True)
