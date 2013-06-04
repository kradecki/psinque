# -*- coding: utf-8 -*-
import os
import logging
import webapp2

from google.appengine.api import users

from MasterHandler import MasterHandler

availableLanguages = {
                      'en': 'English',
                      'pl': 'Polski',
                      'de': 'Deutsch',
                     }

#-----------------------------------------------------------------------------

class UserSettings(db.Model):
  '''User settings other than those stored in the profile'''
  user = db.UserProperty()
 
  # Settings:
  preferredLanguage = db.StringProperty(choices = availableLanguages.keys(),
                                        default = 'en')  # availableLanguages.keys()[0] is 'de', they seem to be sorted alphabetically
  notifyNewsletter = db.BooleanProperty(default = False)   # I _never_ ask for newsletters, so why force it on the users?
  notifyEmails = db.BooleanProperty(default = True)
  notifyStopsUsingMyPrivateData = db.BooleanProperty(default = True)
  notifyAsksForPrivateData = db.BooleanProperty(default = True)
  notifyAllowsMePrivateData = db.BooleanProperty(default = True)
  notifyDisallowsMePrivateData = db.BooleanProperty(default = True)
  notifyRequestDecision = db.BooleanProperty(default = True)
  
  cardDAVenabled = db.BooleanProperty(default = False)
  syncWithGoogle = db.BooleanProperty(default = False)

#-----------------------------------------------------------------------------

class Settings(MasterHandler):

  def getUserSettings(user):
      return UserSettings.all().filter("user =", user).get()

  def get(self):
    userSettings = self.getUserSettings(users.get_current_user())
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

#-----------------------------------------------------------------------------

app = webapp2.WSGIApplication([
  ('/settings', Settings)
], debug=True)
