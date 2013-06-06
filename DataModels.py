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

    canViewName = db.BooleanProperty(default = True)
    canViewBirthday = db.BooleanProperty(default = False)
    canViewGender = db.BooleanProperty(default = False)

    vcard = db.TextProperty()   # vCard for CardDAV access; it's not a StringProperty
                        # because it might be longer than 500 characters
    vcardMTime = db.StringProperty() # modification time
    vcardMD5 = db.StringProperty()   # MD5 checksum of the vcard
    
    @property
    def permitEmails(self):
        return PermitEmail.all().ancestor(self)
    
    def generateVCard(self):
        
        logging.info("Generating vCard")
        userProfile = self.parent()
        newVCard = vCard.VCard()
        
        if self.canViewName:
            newVCard.addNames(u",".join(userProfile.givenNames),
                              u",".join(userProfile.familyNames))
        else:
            newVCard.addNames(u"", u"")

            
        for email in userProfile.emails:
            permitEmail = PermitEmail.all().ancestor(self).filter("userEmail =", email).get()
            if permitEmail.canView:
                newVCard.addEmail(email.email, email.emailType)
        
        newVCard = db.Text(newVCard.serialize())
        
        if newVCard != self.vcard:
            logging.info("Updating vCard")
            self.vcard = newVCard
            self.vcardMTime = str(datetime.date(datetime.now())) + "." + str(datetime.time(datetime.now()))
            self.vcardMD5 = md5.new(self.vcard.encode('utf8')).hexdigest()


#-----------------------------------------------------------------------------

class Group(db.Model):
    
    name = db.StringProperty()
    sync = db.BooleanProperty(default = True)


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

    # Shortcuts to non-removable permits
    defaultPermit = db.ReferenceProperty(Permit,
                                         collection_name = "userProfile1")
    publicPermit = db.ReferenceProperty(Permit,
                                        collection_name = "userProfile2")
    
    publicEnabled = db.BooleanProperty(default = False)

    @property
    def fullName(self):
        if not middleName is None:
            return self.firstName + " " + \
                   self.middleName + " " + \
                   self.lastName
        else:
            return self.firstName + " " + \
                   self.lastName
     
    @property
    def emails(self):
        return UserEmail.all().ancestor(self).order("-primary")

    @property
    def addresses(self):
        return UserAddress.all().ancestor(self)

#class UserPhoto(db.Model):
  #user = db.ReferenceProperty(UserProfile, collection_name = "photos")
  #photograph = blobstore.BlobReferenceProperty()

#-----------------------------------------------------------------------------

class Psinque(db.Model):
    
    fromUser = db.ReferenceProperty(UserProfile,
                                    collection_name = "outgoing")
    #toUser   = db.ReferenceProperty(UserProfile,
                                    #collection_name = "incoming")
    
    status = db.StringProperty(choices = ["pending", "established", "banned"])
    private = db.BooleanProperty(default = False)

    creationTime = db.DateTimeProperty(auto_now = True)
  
#-----------------------------------------------------------------------------

class Contact(db.Model):

    incoming = db.ReferenceProperty(Psinque,
                                    collection_name = "contact1")
    incomingPrivate = db.BooleanProperty()
    incomingPending = db.BooleanProperty()

    outgoing = db.ReferenceProperty(Psinque,
                                    collection_name = "contact2")
    outgoingPrivate = db.BooleanProperty()
    outgoingPending = db.BooleanProperty()

    friend = db.ReferenceProperty(UserProfile)
    
    group = db.ReferenceProperty(Group)
    permit = db.ReferenceProperty(Permit)

    displayName = db.StringProperty()
    creationTime = db.DateTimeProperty(auto_now = True)

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

availableLanguages = {
                      'en': 'English',
                      'pl': 'Polski',
                      'de': 'Deutsch',
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

class CardDAVLogin(db.Model):
    name = db.StringProperty()
    generatedUsername = db.StringProperty()
    generatedPassword = db.StringProperty()

#-----------------------------------------------------------------------------
