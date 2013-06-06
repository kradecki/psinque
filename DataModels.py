# -*- coding: utf-8 -*-

from google.appengine.ext import db

#-----------------------------------------------------------------------------

class Permit(db.Model):
    
    name = db.StringProperty()
    public = db.BooleanProperty(default = False)

    canViewName = db.BooleanProperty(default = True)
    canViewBirthday = db.BooleanProperty(default = False)
    canViewGender = db.BooleanProperty(default = False)

    vcard = db.Text()   # vCard for CardDAV access; it's not a StringProperty
                        # because it might be longer than 500 characters
    vcardMTime = db.StringProperty() # modification time
    vcardMD5 = db.StringProperty()   # MD5 checksum of the vcard
    
    def generateVCard(self):
        
        userProfile = self.parent()
        newVCard = vCard()
        newVCard.add('n')
        newVCard.n.value = userProfile.name
        newVCard.add('fn')
        newVCard.fn.value = userProfile.fullName
        if userProfile.companyName:
            newVCard.add('org')
            newVCard.org.value = userProfile.companyName
        for email in userProfile.emails:
            newVCard.add('email')
            newVCard.email.value = email.email
            newVCard.email.type_param = email.emailType  #TODO: convert to vCard type names?
        
        self.vcard = newVCard.serialize()
        self.vcardMTime = str(datetime.date(datetime.now())) + "-" + str(datetime.time(datetime.now()))
        self.vcardMD5 = md5.new(self.vcard).hexdigest()


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
    lastName = db.StringProperty()
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
    def vcardName(self):
        vcard.Name(family = self.lastName,
                   given = self.givenNames[0])

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
  #user = db.ReferenceProperty(UserProfile, collection_name = "addresses")
  address = db.PostalAddressProperty()
  city = db.StringProperty()
  postalCode = db.StringProperty()
  addressType = db.StringProperty(choices = addressTypes.keys())
  location = db.GeoPtProperty()

#-----------------------------------------------------------------------------

class UserEmail(db.Model):
  #user = db.ReferenceProperty(UserProfile, collection_name = "emails")
  email = db.EmailProperty()
  emailType = db.StringProperty(choices = emailTypes.keys())
  primary = db.BooleanProperty()

#-----------------------------------------------------------------------------

class UserIM(db.Model):
  #user = db.ReferenceProperty(UserProfile)
  im = db.IMProperty()

#-----------------------------------------------------------------------------

class UserPhoneNumber(db.Model):
  #user = db.ReferenceProperty(UserProfile, collection_name = "phoneNumbers")
  phone = db.PhoneNumberProperty(required = True)
  phoneType = db.StringProperty(choices = phoneTypes)

#-----------------------------------------------------------------------------

class UserWebpage(db.Model):
  #user = db.ReferenceProperty(UserProfile)
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
