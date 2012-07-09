
import os
import logging

from google.appengine.ext import webapp
from google.appengine.api import users
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.ext.webapp import template

from MasterHandler import MasterHandler

class StartPage(webapp.RequestHandler):
  def get(self):
    user = users.get_current_user()
    if not user:    # user not logged in
        self.redirect("/login")
    else:
        self.redirect('/profile')

class Login(webapp.RequestHandler):
  def get(self):
    self.response.out.write(template.render(os.path.join(os.path.dirname(__file__), "templates/login.html"),
                                            {'loginurl': users.create_login_url("/profile")}
                                           ))

class ViewProfile(MasterHandler):
  def get(self):
    MasterHandler.sendTopTemplate(self, activeEntry = "Visiting card")
    self.response.out.write('<div id="content">Under construction...</div')
    MasterHandler.sendBottomTemplate(self)

application = webapp.WSGIApplication([
  ('/', StartPage),
  ('/login', Login),
  ('/profile', ViewProfile)
], debug=True)

def main():
  run_wsgi_app(application)

if __name__ == '__main__':
  main()
