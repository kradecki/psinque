
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
      }
    else:
      template_values = {
        'preferredLanguage': 'user not found',
      }
    MasterHandler.sendTopTemplate(self, activeEntry = "Settings")
    MasterHandler.sendContent(self, 'templates/viewSettings.html', template_values)
    MasterHandler.sendBottomTemplate(self)

class SaveSettings(MasterHandler):

  def get(self):
    MasterHandler.sendTopTemplate(self, activeEntry = "Settings")
    self.response.out.write('<div id="content">Under construction</div>')
    MasterHandler.sendBottomTemplate(self)

application = webapp.WSGIApplication([
  ('/settings', Settings),
  ('/savesettings', SaveSettings)
], debug=True)

def main():
  run_wsgi_app(application)

if __name__ == '__main__':
  main()
