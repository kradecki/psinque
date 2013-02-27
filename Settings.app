# -*- coding: utf-8 -*-
import os
import logging
import webapp2

from google.appengine.api import users

from MasterHandler import MasterHandler

from users.UserDataModels import UserProfile, UserSettings, availableLanguages

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
    MasterHandler.sendContent(self, 'templates/settings_viewSettings.html', template_values)
    MasterHandler.sendBottomTemplate(self)

  def post(self):
    user = users.get_current_user()
    query = UserSettings.all()
    userSettings = query.filter("user =", user).get()
    userSettings.preferredLanguage = self.request.get('language')
    userSettings.notifyOnNewsletter = bool(self.request.get('newsletter'))
    logging.info(u"Wartość =" + unicode(self.request.get('newsletter')))
    userSettings.put()

    self.redirect('/settings')  # redirects to Settings

application = webapp2.WSGIApplication([
  ('/settings', Settings)
], debug=True)
