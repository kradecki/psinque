
import os
import logging

from google.appengine.ext import webapp
from google.appengine.api import users
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.ext.webapp import template

from MasterHandler import MasterHandler

from UserDataModels import UserProfile, UserSettings, availableLanguages

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

application = webapp.WSGIApplication([
  ('/', StartPage),
  ('/login', Login),
], debug=True)

def main():
  run_wsgi_app(application)

if __name__ == '__main__':
  main()
