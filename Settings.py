# -*- coding: utf-8 -*-

import os
import logging
import webapp2
import random
import string

from google.appengine.api import users

from MasterHandler import MasterHandler
from CardDAV import CardDAVPassword

from DataModels import UserSettings

#-----------------------------------------------------------------------------
# Request handler

class Settings(MasterHandler):

    #****************************
    # Private methods
    # 
    
    passwordCharacters = string.ascii_uppercase + string.ascii_lowercase + string.digits + '_'
    
    def _getUserSettings(self):
        
        return UserSettings.all(). \
                            ancestor(self.userProfile). \
                            get()
                            
                            
    def _generateRandomSequence(self, passwordLength):
        
        return "".join([random.SystemRandom().choice(self.passwordCharacters) for x in range(passwordLength)])
        
        

    #****************************
    # Views
    # 
    
    def view(self):
        
        if self.getUserProfile():
            
            userSettings = self._getUserSettings()
            
            carddavLogins = CardDAVLogin.all().ancestor(self.userProfile)
            
            self.sendTopTemplate(activeEntry = "Settings")
            self.sendContent('templates/settings_viewSettings.html', {
                'userSettings': userSettings,
                'carddavLogins': carddavLogins,
                'availableLanguages': availableLanguages,
            })
            self.sendBottomTemplate()

    #****************************
    # AJAX methods
    # 
    
    def updatesettings(self):
        
        if self.getUserProfile():
            raise AjaxError("User profile not found")

        userSettings = self._getUserSettings()
        if userSettings.parent() != self.userProfile:
            raise AjaxError("You don't own these settings")
        
        userSettings.preferredLanguage = self.getRequiredParameter('language')
        userSettings.notifyNewsletter = self.getRequiredBoolParameter('newsletter')
        userSettings.notifyEmails = self.getRequiredBoolParameter('emailnotifications')
        userSettings.cardDAVenabled = self.getRequiredBoolParameter('synccarddav')
        userSettings.syncWithGoogle = self.getRequiredBoolParameter('syncgoogle')
        userSettings.put()

        self.sendJsonOK()
        
        
    def generatecarddavlogin(self):
        
        if self.getUserProfile():
            raise AjaxError("User profile not found")
        
        carddavName = self.getRequiredParameter("name")
        
        while True:
            generatedUsername = self._generateRandomSequence(6)
            if not CardDAVPassword.all().filter("generatedUsername =", generatedUsername).get():
                break

        # With 62 password characters, the entropy of a 14-character password is 71 bits,
        # which is reasonably difficult to hack
        cardDAVPassword = CardDAVPassword(parent = self.userProfile,
                                          name = carddavName,
                                          generatedUsername = generatedUsername,
                                          generatedPassword = self._generateRandomSequence(12))
        cardDAVPassword.put()
        
        self.sendJsonOK()

        
    def deletecarddav(self):
        
        if self.getUserProfile():
            raise AjaxError("User profile not found")
        
        cardDAVPassword = CardDAVPassword.get(self.getRequiredParameter("key"))
        if cardDAVPassword.parent() != self.userProfile:
            raise AjaxError("You don't own these CardDAV credentials")
        
        cardDAVPassword.delete()

        self.sendJsonOK()
        

#-----------------------------------------------------------------------------

app = webapp2.WSGIApplication([
  ('/settings/(\w+)', Settings)
], debug=True)
