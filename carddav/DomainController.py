
import os.path
import logging
import md5

import CardDAV

class PsinqueDomainController(object):
    
    
    def __init__(self, userMap = None):
        
        self.userMap = userMap
    
    
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
        return (realmname == "carddav")
           
    
    def getRealmUserPassword(self, realmname, username, environ):
        """
        Return the password for the given username for the realm.
        Used for digest authentication.
        """
        #if self.userPassword is None:  # user has not generated password
            #return None
        carddav_password = CardDAV.getCardDAVLogin(username)
        if carddav_password is None:
            return [ u"", u"" ]
        else:
            return [ carddav_password.generatedPasswordHash, carddav_password.salt ]
    
    
    def authDomainUser(self, realmname, username, password, environ):
        """
        Returns True if this username/password pair is valid for the realm, 
        False otherwise. Used for basic authentication.
        """
        if realmname != "carddav":
            return False

        userPassword = CardDAV.getCardDAVLogin(username)
        
        if userPassword is None:
            return False
          
        passwordHash = md5.new(userPassword.salt + password).hexdigest()
        
        return (userPassword.generatedPasswordHash == passwordHash)

