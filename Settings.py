# -*- coding: utf-8 -*-
import os
import logging
import webapp2

from google.appengine.api import users

from MasterHandler import MasterHandler

from users.UserManagement import getUserSettings
from users.UserDataModels import UserProfile, UserSettings, availableLanguages

class Settings(MasterHandler):

  def get(self):
    userSettings = getUserSettings(users.get_current_user())
    if not userSettings is None:
        template_values = {
          'preferredLanguage': userSettings.preferredLanguage,
          'availableLanguages': availableLanguages,
          'notifyNewsletter': userSettings.notifyNewsletter,
          'notifyEmails': userSettings.notifyEmails,
          'cardDAVenabled': userSettings.cardDAVenabled,
          'syncWithGoogle': userSettings.syncWithGoogle,
        }
        MasterHandler.sendTopTemplate(self, activeEntry = "Settings")
        MasterHandler.sendContent(self, 'templates/settings_viewSettings.html', template_values)
        MasterHandler.sendBottomTemplate(self)
    else:
      self.redirect('/login')  #TODO: Create settings for the user?

  def post(self):
    userSettings = getUserSettings(users.get_current_user())
    userSettings.preferredLanguage = self.request.get('language')
    userSettings.notifyNewsletter = bool(self.request.get('newsletter'))
    userSettings.notifyEmails = bool(self.request.get('emailnotifications'))
    userSettings.cardDAVenabled = bool(self.request.get('synccarddav'))
    userSettings.syncWithGoogle = bool(self.request.get('syncgoogle'))
    userSettings.put()

    self.redirect('/settings')  # redirects to Settings

app = webapp2.WSGIApplication([
  ('/settings', Settings)
], debug=True)
