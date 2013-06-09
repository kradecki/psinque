
import os.path
import logging

import CardDAV

class PsinqueDomainController(object):
    
    
    def __init__(self, userMap = None):
        
        self.userMap = userMap
        self.userPassword = u""
    
    
    def __repr__(self):
        
        return self.__class__.__name__
    
    
    def getDomainRealm(self, inputURL, environ):
        """
        Resolve a relative url to the appropriate realm name.
        """
        return "carddav"  # we only have one realm
    
    
    def requireAuthentication(self, realmname, environ):
        """
        Return True if this realm requires authentication or False if it is 
        available for general access.
        """
        return True  # always required
    
    
    def isRealmUser(self, realmname, username, environ):
        """
        Returns True if this username is valid for the realm, False otherwise.
        Used for digest authentication.
        """
        if realmname != "carddav":
            return False
        
        if self.userPassword is None:  # user has not generated password
            return False
        
        if self.userPassword == u"":   # we haven't checked the user yet

            self.userPassword = CardDAV.getCardDAVLogin(username)

            if self.userPassword is None:
                return False
            
        return True
   
    
    def getRealmUserPassword(self, realmname, username, environ):
        """
        Return the password for the given username for the realm.
        Used for digest authentication.
        """
        if self.userPassword is None:  # user has not generated password
            return None
        if self.userPassword == u"":   # we haven't checked the user yet
            self.userPassword = CardDAV.getCardDAVLogin(username)
        logging.info(self.userPassword.generatedPassword)
        return self.userPassword.generatedPassword
    
    
    def authDomainUser(self, realmname, username, password, environ):
        """
        Returns True if this username/password pair is valid for the realm, 
        False otherwise. Used for basic authentication.
        """
        if realmname != "carddav":
            return False
        if self.userPassword is None:  # user has not generated password
            return False
        if self.userPassword == u"":   # we haven't checked the user yet
            self.userPassword = CardDAV.getCardDAVLogin(username)
            if self.userPassword is None:
                return False
        return self.userPassword == password

