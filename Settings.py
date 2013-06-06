# -*- coding: utf-8 -*-
import os
import logging
import webapp2

from google.appengine.api import users

from MasterHandler import MasterHandler

#-----------------------------------------------------------------------------
# Data models

availableLanguages = {
                      'en': 'English',
                      'pl': 'Polski',
                      'de': 'Deutsch',
                     }

class UserSettings(db.Model):
    '''
    User settings other than those stored in the UserProfile.
    '''
    #user = db.UserProperty()

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
    #syncWithGoogle = db.BooleanProperty(default = False)

#-----------------------------------------------------------------------------
# Request handler

class Settings(MasterHandler):

    #****************************
    # Private methods
    # 
    

    #****************************
    # Views
    # 
    
    def view(self):
        
        if self.getUserProfile():
            
            userSettings = UserSettings.all().
                                        ancestor(self.userProfile).
                                        get()
            
            self.sendTopTemplate(activeEntry = "Settings")
            self.sendContent('templates/settings_viewSettings.html', {
                'userSettings': userSettings,
                'availableLanguages': availableLanguages,
            })
            self.sendBottomTemplate()

    #****************************
    # AJAX methods
    # 
    
    def updatesettings(self):
        
        userSettings = getUserSettings(users.get_current_user())
        userSettings.preferredLanguage = self.getRequiredParameter('language')
        userSettings.notifyNewsletter = self.getRequiredBoolParameter('newsletter')
        userSettings.notifyEmails = self.getRequiredBoolParameter('emailnotifications')
        userSettings.cardDAVenabled = self.getRequiredBoolParameter('synccarddav')
        userSettings.syncWithGoogle = self.getRequiredBoolParameter('syncgoogle')
        userSettings.put()

        self.redirect('/settings')  # redirects to Settings
        
    def generatecarddavlogin(self):
        
        raise AjaxError("Unimplemented")

#-----------------------------------------------------------------------------

app = webapp2.WSGIApplication([
  ('/settings/(\w+)', Settings)
], debug=True)
