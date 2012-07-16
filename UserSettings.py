
import os
import logging

from google.appengine.ext import webapp
from google.appengine.api import users
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.ext.webapp import template

from MasterHandler import MasterHandler

from UserDataModels import UserProfile, UserSettings, availableLanguages

class Settings(MasterHandler):

  def get(self):
    user = users.get_current_user()
    query = UserSettings.all()
    userSettings = query.filter("user =", user).get()
    if not userSettings == None:
      template_values = {
        'preferredLanguage': userSettings.preferredLanguage,
        'availableLanguages': availableLanguages,
      }
    else:
      template_values = {
        'preferredLanguage': 'user not found',
        'availableLanguages': availableLanguages,
      }
    MasterHandler.sendTopTemplate(self, activeEntry = "Settings")
    MasterHandler.sendContent(self, 'templates/viewSettings.html', template_values)
    MasterHandler.sendBottomTemplate(self)

  def post(self):
    user = users.get_current_user()
    query = UserSettings.all()
    userSettings = query.filter("user =", user).get()

application = webapp.WSGIApplication([
  ('/settings', Settings)
], debug=True)

def main():
  run_wsgi_app(application)

if __name__ == '__main__':
  main()
