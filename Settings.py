# -*- coding: utf-8 -*-

import os
import logging
import webapp2
import random
import string

from google.appengine.api import users

from MasterHandler import MasterHandler, AjaxError
from DataModels import UserSettings, CardDAVLogin
from DataModels import availableLanguages

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
        
        if not self.getUserProfile():
            raise AjaxError("User profile not found")

        userSettings = self._getUserSettings()
        if userSettings.parent().key() != self.userProfile.key():
            raise AjaxError("You don't own these settings")
        
        userSettings.preferredLanguage = self.getRequiredParameter('language')
        userSettings.notifyNewsletter = self.getRequiredBoolParameter('newsletter')
        userSettings.notifyEmails = self.getRequiredBoolParameter('emailnotifications')
        userSettings.cardDAVenabled = self.getRequiredBoolParameter('synccarddav')
        #userSettings.syncWithGoogle = self.getRequiredBoolParameter('syncgoogle')
        userSettings.put()

        self.sendJsonOK()
        
        
    def generatecarddavlogin(self):
        
        if not self.getUserProfile():
            raise AjaxError("User profile not found")
        
        carddavName = self.getRequiredParameter("name")
        
        while True:
            generatedUsername = self._generateRandomSequence(6)
            if not CardDAVLogin.all().filter("generatedUsername =", generatedUsername).get():
                break

        # With 62 password characters, the entropy of a 14-character password is 71 bits,
        # which is reasonably difficult to hack
        generatedPassword = self._generateRandomSequence(12)
        cardDAVLogin = CardDAVLogin(parent = self.userProfile,
                                    name = carddavName,
                                    generatedUsername = generatedUsername,
                                    generatedPassword = generatedPassword)
        cardDAVLogin.put()
        
        self.sendJsonOK({
            "username": generatedUsername,
            "password": generatedPassword,
        })

        
    def deletecarddav(self):
        
        if not self.getUserProfile():
            raise AjaxError("User profile not found")
        
        cardDAVLogin = CardDAVLogin.get(self.getRequiredParameter("key"))
        
        logging.info(cardDAVLogin.parent())
        logging.info(self.userProfile.key())
        
        if cardDAVLogin.parent().key() != self.userProfile.key():
            raise AjaxError("You don't own these CardDAV credentials")
        
        cardDAVLogin.delete()

        self.sendJsonOK()
        

#-----------------------------------------------------------------------------

app = webapp2.WSGIApplication([
  ('/settings/(\w+)', Settings)
], debug=True)

