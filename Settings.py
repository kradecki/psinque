# -*- coding: utf-8 -*-

import os
import logging
import webapp2
import random
import string
import md5

from google.appengine.api import users

from MasterHandler import MasterHandler, AjaxError
from DataModels import UserSettings, CardDAVLogin
from DataModels import availableLanguages
from Security import psinqueMD5

#-----------------------------------------------------------------------------
# Request handler

class Settings(MasterHandler):

    #****************************
    # Private methods
    # 
    
    passwordCharacters = string.ascii_lowercase
    
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
            
            carddavLogins = CardDAVLogin.all(). \
                                         ancestor(self.userProfile). \
                                         fetch(1000)
            
            self.sendContent('templates/Settings.html',
                            activeEntry = "Settings",
                            templateVariables = {
                'userSettings': userSettings,
                'carddavLogins': carddavLogins,
                'availableLanguages': availableLanguages,
            })


    #****************************
    # AJAX methods
    # 
    
    def updatesettings(self):
        
        userSettings = self._getUserSettings()
        if userSettings.parent().key() != self.userProfile.key():
            raise AjaxError("You don't own these settings")
        
        userSettings.preferredLanguage = self.getRequiredParameter('language')
        userSettings.notifyNewsletter = self.getRequiredBoolParameter('newsletter')

        userSettings.notifyEmails = self.getRequiredBoolParameter('emailnotifications')
        userSettings.notifyStopsUsingMyPrivateData = self.getRequiredBoolParameter('notifystops')
        userSettings.notifyAsksForPrivateData = self.getRequiredBoolParameter('notifyasks')
        userSettings.notifyAllowsMePrivateData = self.getRequiredBoolParameter('notifyaccepts')
        userSettings.notifyDisallowsMePrivateData = self.getRequiredBoolParameter('notifyrejects')
        userSettings.notifyRequestDecision = self.getRequiredBoolParameter('notifyrevokes')

        userSettings.cardDAVenabled = self.getRequiredBoolParameter('synccarddav')
        #userSettings.syncWithGoogle = self.getRequiredBoolParameter('syncgoogle')

        userSettings.put()

        self.sendJsonOK()
        
        
    def generatecarddavlogin(self):
              
        carddavName = self.getRequiredParameter("name")
        
        while True:
            generatedUsername = self._generateRandomSequence(8)
            if not CardDAVLogin.all().filter("generatedUsername =", generatedUsername).get():
                break

        generatedPassword = self._generateRandomSequence(16)
        salt = self._generateRandomSequence(2)
        
        cardDAVLogin = CardDAVLogin(parent = self.userProfile,
                                    name = carddavName,
                                    generatedUsername = generatedUsername,
                                    generatedPasswordHash = md5.new(salt + generatedPassword).hexdigest(),
                                    salt = salt)
        cardDAVLogin.put()
        
        self.sendJsonOK({
            "key": str(cardDAVLogin.key()),
            "username": generatedUsername,
            "password": generatedPassword,
        })

        
    def deletecarddav(self):
        
        cardDAVLogin = CardDAVLogin.get(self.getRequiredParameter("key"))
        
        logging.info(cardDAVLogin.parent())
        logging.info(self.userProfile.key())
        
        if cardDAVLogin.parent().key() != self.userProfile.key():
            raise AjaxError("You don't own these CardDAV credentials")
        
        cardDAVLogin.delete()

        self.sendJsonOK()
        

#-----------------------------------------------------------------------------

app = webapp2.WSGIApplication([
  (r'/settings/(\w+)', Settings)
], debug=True)

