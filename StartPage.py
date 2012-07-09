
import os
import logging

from google.appengine.ext import webapp
from google.appengine.api import users
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.ext.webapp import template

from UserDataModels import UserProfile

class StartPage(DictionaryHandler):

  def get(self):

    user = users.get_current_user()
    if not user:    # user not logged in
        self.redirect('/login')
    else:
        self.redirect('/profile')

application = webapp.WSGIApplication([
  ('/', StartPage),
  ('/login', Login),
  ('/profile', ViewProfile)
], debug=True)

def main():
  run_wsgi_app(application)

if __name__ == '__main__':
  main()
