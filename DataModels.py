# -*- coding: utf-8 -*-

from google.appengine.ext import db

import logging

import vCard
from datetime import datetime
import md5

#-----------------------------------------------------------------------------

class Permit(db.Model):
    
    name = db.StringProperty()
    public = db.BooleanProperty(default = False)

    canViewFirstNames = db.BooleanProperty(default = True)
    canViewLastNames = db.BooleanProperty(default = True)
    canViewBirthday = db.BooleanProperty(default = False)
    canViewGender = db.BooleanProperty(default = False)

    vcard = db.TextProperty()   # vCard for CardDAV access; it's not a StringProperty
                                # because it might be longer than 500 characters
    vcardMTime = db.StringProperty() # modification time
    vcardMD5 = db.StringProperty()   # MD5 checksum of the vcard
    
    displayName = db.StringProperty()
    
    @property
    def permitEmails(self):
        return PermitEmail.all().ancestor(self)
    
    def _getFirstNames(self, userProfile):
        if self.canViewFirstNames:
            return userProfile.givenNames
        else:
            return []
    
    def _getLastNames(self, userProfile):
        if self.canViewLastNames:
            return userProfile.familyNames
        else:
            return []
    
    def _updateDisplayName(self, firstNames, lastNames):
        displayName = u""
        if len(firstNames) > 0:
            displayName = displayName + u" ".join(firstNames)
        if len(lastNames) > 0:
            if displayName != u"":
                displayName = displayName + u" "
            displayName = displayName + u" ".join(lastNames)
        self.displayName = displayName
        if self.displayName == u"":
            for permitEmail in self.permitEmails:
                if permitEmail.canView:
                    self.displayName = permitEmail.userEmail.mail
                    return
    
    def generateVCard(self):
        
        logging.info("Generating vCard")
        userProfile = self.parent()
        newVCard = vCard.VCard()

        firstNames = self._getFirstNames(userProfile)
        lastNames = self._getLastNames(userProfile)
        newVCard.addNames(u", ".join(firstNames),
                          u", ".join(lastNames))

        for email in userProfile.emails:
            permitEmail = email.permitEmails.get()
            if permitEmail.canView:
                newVCard.addEmail(email.email, email.emailType)
        
        newVCard = db.Text(newVCard.serialize())
        
        if newVCard != self.vcard:
            logging.info("Updating vCard")
            self.vcard = newVCard
            self.vcardMTime = str(datetime.date(datetime.now())) + "." + str(datetime.time(datetime.now()))
            self.vcardMD5 = md5.new(self.vcard.encode('utf8')).hexdigest()
            
        self._updateDisplayName(firstNames, lastNames)


#-----------------------------------------------------------------------------

class Group(db.Model):
    
    name = db.StringProperty()
    sync = db.BooleanProperty(default = True)

#-----------------------------------------------------------------------------

availableLanguages = {
    'en': u'English',
    'pl': u'Polski',
    'de': u'Deutsch',
    'jp': u'日本語',
}

class UserSettings(db.Model):
    '''
    User settings other than those stored in the UserProfile.
    '''
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

genders    = ["male", "female"]
phoneTypes = ["home landline", "private cellphone", "work cellphone", "work landline", "home fax", "work fax", "other"]
addressTypes = {'home': 'Home', 'work': 'Work'}
emailTypes   = {'private': 'Private', 'work': 'Work'}

class UserProfile(db.Model):

    user = db.UserProperty()

    givenNames = db.StringListProperty()
    familyNames = db.StringListProperty()
    pseudonyms = db.StringListProperty()
    companyName = db.StringProperty()

    gender = db.StringProperty(choices = genders)

    birthDay = db.DateProperty()  

    publicEnabled = db.BooleanProperty(default = False)

    # Shortcuts to non-removable permits
    defaultPermit = db.ReferenceProperty(Permit,
                                         collection_name = "userProfile1")
    publicPermit = db.ReferenceProperty(Permit,
                                        collection_name = "userProfile2")
    defaultGroup = db.ReferenceProperty(Group)
    
    userSettings = db.ReferenceProperty(UserSettings)
    
    @property
    def emails(self):
        return UserEmail.all().ancestor(self).order("-primary")

    @property
    def addresses(self):
        return UserAddress.all().ancestor(self)
    
    @property
    def permits(self):
        return Permit.all().ancestor(self)

#class UserPhoto(db.Model):
  #user = db.ReferenceProperty(UserProfile, collection_name = "photos")
  #photograph = blobstore.BlobReferenceProperty()

#-----------------------------------------------------------------------------

class Psinque(db.Model):
    
    fromUser = db.ReferenceProperty(UserProfile,
                                    collection_name = "outgoing")
    
    status = db.StringProperty(choices = ["pending", "established", "banned"])
    private = db.BooleanProperty(default = False)

    creationTime = db.DateTimeProperty(auto_now = True)
    
    permit = db.ReferenceProperty(Permit)
    
    @property
    def displayName(self):
        if not self.permit is None:
            return self.permit.displayName
        return self.fromUser.publicPermit.displayName
  
#-----------------------------------------------------------------------------

class Contact(db.Model):

    incoming = db.ReferenceProperty(Psinque,
                                    collection_name = "contact1")   
    outgoing = db.ReferenceProperty(Psinque,
                                    collection_name = "contact2")

    friend = db.ReferenceProperty(UserProfile)
    friendsContact = db.SelfReferenceProperty()
    
    group = db.ReferenceProperty(Group)
    permit = db.ReferenceProperty(Permit)

    creationTime = db.DateTimeProperty(auto_now = True)

    @property
    def displayName(self):
        if not self.incoming is None:
            return self.incoming.displayName
        return self.friendsContact.permit.displayName
  
#-----------------------------------------------------------------------------

class UserAddress(db.Model):
    address = db.PostalAddressProperty()
    city = db.StringProperty()
    postalCode = db.StringProperty()
    addressType = db.StringProperty(choices = addressTypes.keys())
    location = db.GeoPtProperty()

#-----------------------------------------------------------------------------

class UserEmail(db.Model):
    email = db.EmailProperty()
    emailType = db.StringProperty(choices = emailTypes.keys())
    primary = db.BooleanProperty(default = False)

#-----------------------------------------------------------------------------

class UserIM(db.Model):
    im = db.IMProperty()

#-----------------------------------------------------------------------------

class UserPhoneNumber(db.Model):
    phone = db.PhoneNumberProperty(required = True)
    phoneType = db.StringProperty(choices = phoneTypes)

#-----------------------------------------------------------------------------

class UserWebpage(db.Model):
    address = db.StringProperty()
    webpageType = db.StringProperty(choices = ["private homepage", "business homepage", "facebook", "myspace", "other"])

#-----------------------------------------------------------------------------

class PermitEmail(db.Model):
    userEmail = db.ReferenceProperty(UserEmail,
                                     collection_name = "permitEmails")
    canView = db.BooleanProperty(default = False)


#-----------------------------------------------------------------------------

class CardDAVLogin(db.Model):
    name = db.StringProperty()
    generatedUsername = db.StringProperty()
    generatedPassword = db.StringProperty()

#-----------------------------------------------------------------------------
