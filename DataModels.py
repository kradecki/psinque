# -*- coding: utf-8 -*-

from google.appengine.ext import db

import logging

import vCard
import datetime
import md5

#-----------------------------------------------------------------------------

genders      = ["Male", "Female", "Undisclosed"]
privacyTypes = ['Home', 'Work']
phoneTypes   = ["Landline", "Cellphone", "Fax", "Other"]
wwwTypes     = ["Personal", "Company", "MySpace", "Facebook"]

monthNames = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']

imTypes = {
    'Google Talk': 'http://talk.google.com/',
    'Skype': 'http://www.skype.com/',
    'Gadu-gadu': 'http://gadu-gadu.pl/',
    'MSN Messanger': 'http://messenger.msn.com/',
    'Yahoo! Messanger': 'http://messenger.yahoo.com/',
}

availableLanguages = {
    u'English': 'en',
    u'Polski': 'pl',
    u'Deutsch': 'de',
    u'日本語': 'jp',
}

#-----------------------------------------------------------------------------

class Permit(db.Model):
    
    name = db.StringProperty()
    public = db.BooleanProperty(default = False)

    canViewGivenNames = db.BooleanProperty(default = True)
    canViewFamilyNames = db.BooleanProperty(default = True)
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
    
    
    @property
    def permitIMs(self):
        return PermitEmail.all().ancestor(self)
    
    
    @property
    def permitWWWs(self):
        return PermitEmail.all().ancestor(self)
    
    
    @property
    def permitPhones(self):
        return PermitEmail.all().ancestor(self)
    
    
    @property
    def permitAddresses(self):
        return PermitEmail.all().ancestor(self)
    
    
    def _getGivenNames(self, userProfile):
        if self.canViewGivenNames:
            return userProfile.givenNames
        else:
            return ""
    
    
    def _getFamilyNames(self, userProfile):
        if self.canViewFamilyNames:
            return userProfile.familyNames
        else:
            return ""
    
    
    def _updateDisplayName(self, givenNames, familyNames):
        displayName = u""
        if givenNames != u"":
            displayName = displayName + givenNames
        if familyNames != u"":
            if displayName != u"":
                displayName = displayName + u" "
            displayName = displayName + familyNames
        self.displayName = displayName
        if self.displayName == u"":
            for permitEmail in self.permitEmails:
                if permitEmail.canView:
                    self.displayName = permitEmail.userEmail.email
                    return
    
    
    def generateVCard(self):
        
        logging.info("Generating vCard")
        userProfile = self.parent()
        newVCard = vCard.VCard()

        givenNames = self._getGivenNames(userProfile)
        familyNames = self._getFamilyNames(userProfile)
        newVCard.addNames(givenNames, familyNames)

        for email in userProfile.emails:
            permitEmail = email.individualPermits.get()
            if permitEmail.canView:
                newVCard.addEmail(email.email, email.emailType)
        
        newVCard = db.Text(newVCard.serialize())
        
        if newVCard != self.vcard:
            logging.info("Updating vCard")
            self.vcard = newVCard
            self.vcardMTime = str(datetime.datetime.date(datetime.datetime.now())) + "." + str(datetime.datetime.time(datetime.datetime.now()))
            self.vcardMD5 = md5.new(self.vcard.encode('utf8')).hexdigest()
            
        self._updateDisplayName(givenNames, familyNames)


#-----------------------------------------------------------------------------

class Group(db.Model):
    
    name = db.StringProperty()
    sync = db.BooleanProperty(default = True)

#-----------------------------------------------------------------------------

class UserSettings(db.Model):
    '''
    User settings other than those stored in the UserProfile.
    '''
    preferredLanguage = db.StringProperty(choices = availableLanguages.values(),
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

class UserAddress(db.Model):
    address = db.PostalAddressProperty()
    city = db.StringProperty()
    countryCode = db.StringProperty()
    postalCode = db.StringProperty()
    privacyType = db.StringProperty(choices = privacyTypes)
    location = db.GeoPtProperty()
    creationTime = db.DateTimeProperty(auto_now = True)

#-----------------------------------------------------------------------------

class UserEmail(db.Model):
    itemValue = db.EmailProperty()
    privacyType = db.StringProperty(choices = privacyTypes)
    primary = db.BooleanProperty(default = False)
    creationTime = db.DateTimeProperty(auto_now = True)

#-----------------------------------------------------------------------------

class UserIM(db.Model):
    itemValue = db.IMProperty()
    privacyType = db.StringProperty(choices = privacyTypes)
    creationTime = db.DateTimeProperty(auto_now = True)

#-----------------------------------------------------------------------------

class UserPhoneNumber(db.Model):
    itemValue = db.PhoneNumberProperty(required = True)
    itemType = db.StringProperty(choices = phoneTypes)
    privacyType = db.StringProperty(choices = privacyTypes)
    creationTime = db.DateTimeProperty(auto_now = True)

#-----------------------------------------------------------------------------

class UserWebpage(db.Model):
    itemValue = db.StringProperty()
    itemType = db.StringProperty(choices = wwwTypes)
    privacyType = db.StringProperty(choices = privacyTypes)
    creationTime = db.DateTimeProperty(auto_now = True)

#-----------------------------------------------------------------------------

#class UserPhoto(db.Model):
  #photograph = blobstore.BlobReferenceProperty()

#-----------------------------------------------------------------------------

class UserProfile(db.Model):

    user = db.UserProperty()

    givenNames = db.StringProperty(default = u"")
    givenNamesRomanization = db.StringProperty(default = u"")
    
    familyNames = db.StringProperty(default = u"")
    familyNamesRomanization = db.StringProperty(default = u"")
    
    pseudonyms = db.StringListProperty()
    
    companyName = db.StringProperty(default = u"")
    companyNameRomanization = db.StringProperty(default = u"")

    gender = db.StringProperty(choices = genders)

    birthDate = db.DateProperty(default = datetime.date(1900, 1, 1))  

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
    def ims(self):
        return UserIM.all().ancestor(self)
    
    @property
    def webpages(self):
        return UserWebpage.all().ancestor(self)
    
    @property
    def phones(self):
        return UserPhoneNumber.all().ancestor(self)
    
    @property
    def permits(self):
        return Permit.all().ancestor(self)

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

class PermitEmail(db.Model):
    userEmail = db.ReferenceProperty(UserEmail,
                                     collection_name = "individualPermits")
    canView = db.BooleanProperty(default = False)


class PermitIM(db.Model):
    userIM = db.ReferenceProperty(UserIM,
                                  collection_name = "individualPermits")
    canView = db.BooleanProperty(default = False)


class PermitWebpage(db.Model):
    userWebpage = db.ReferenceProperty(UserWebpage,
                                       collection_name = "individualPermits")
    canView = db.BooleanProperty(default = False)


class PermitPhoneNumber(db.Model):
    userPhoneNumber = db.ReferenceProperty(UserPhoneNumber,
                                           collection_name = "individualPermits")
    canView = db.BooleanProperty(default = False)


class PermitAddress(db.Model):
    userAddress = db.ReferenceProperty(UserAddress,
                                       collection_name = "individualPermits")
    canView = db.BooleanProperty(default = False)


#-----------------------------------------------------------------------------

class CardDAVLogin(db.Model):
    name = db.StringProperty()
    generatedUsername = db.StringProperty()
    generatedPassword = db.StringProperty()

#-----------------------------------------------------------------------------
