
from google.appengine.ext import db
from google.appengine.ext import blobstore

#--------------------------------------------------
# User settings

availableLanguages = {
                      'en': 'English',
                      'pl': 'Polski',
                      'de': 'Deutsch',
                     }

class UserSettings(db.Model):
  '''User settings other than those stored in the profile'''
  user = db.UserProperty()
 
  # Settings:
  preferredLanguage = db.StringProperty(choices = availableLanguages.keys(),
                                        default = 'en')  # availableLanguages.keys()[0] is 'de', they seem to be sorted alphabetically
  notifyNewsletter = db.BooleanProperty(default = False)   # I _never_ ask for newsletters, so why force it on the users?
  notifyEmails = db.BooleanProperty(default = True)
  
  cardDAVenabled = db.BooleanProperty(default = False)
  syncWithGoogle = db.BooleanProperty(default = False)

#--------------------------------------------------
# User profile

genders    = ["male", "female"]
phoneTypes = ["home landline", "private cellphone", "work cellphone", "work landline", "home fax", "work fax", "other"]
addressTypes = {'home': 'Home', 'work': 'Work'}
emailTypes   = {'private': 'Private', 'work': 'Work'}

class UserProfile(db.Model):
  '''User profile'''
  user = db.UserProperty()

  firstName = db.StringProperty(required = True,
                                default = "Jan")
  middleName = db.StringProperty(required = False)
  lastName = db.StringProperty(required = True,
                               default = "Kowalski")
  #pseudonym = db.StringProperty(required = False)

  gender = db.StringProperty(choices = genders,
                             required = False)

  birthDay = db.DateProperty()  
  
  # nationality? namesday?

class UserPhoto(db.Model):
  user = db.ReferenceProperty(UserProfile, collection_name = "photos")
  photograph = blobstore.BlobReferenceProperty()

class UserAddress(db.Model):
  user = db.ReferenceProperty(UserProfile, collection_name = "addresses")
  address = db.PostalAddressProperty()
  city = db.StringProperty()
  postalCode = db.StringProperty()
  addressType = db.StringProperty(choices = addressTypes.keys())
  location = db.GeoPtProperty()

class UserEmail(db.Model):
  user = db.ReferenceProperty(UserProfile, collection_name = "emails")
  email = db.EmailProperty()
  emailType = db.StringProperty(choices = emailTypes.keys())
  primary = db.BooleanProperty()

class UserIM(db.Model):
  user = db.ReferenceProperty(UserProfile)
  im = db.IMProperty()

class UserPhoneNumber(db.Model):
  user = db.ReferenceProperty(UserProfile, collection_name = "phoneNumbers")
  phone = db.PhoneNumberProperty(required = True)
  phoneType = db.StringProperty(choices = phoneTypes)

class UserWebpage(db.Model):
  user = db.ReferenceProperty(UserProfile)
  address = db.StringProperty()
  webpageType = db.StringProperty(choices = ["private homepage", "business homepage", "facebook", "myspace", "other"])

#--------------------------------------------------
# Groups of users

class Group(db.Model):
  creator = db.ReferenceProperty(UserProfile, collection_name = "groups")
  name = db.StringProperty()
  canViewName = db.BooleanProperty(default = True)
  #canViewPsuedonym = db.BooleanProperty(default = False)
  canViewBirthday = db.BooleanProperty(default = False)
  canViewGender = db.BooleanProperty(default = False)
  vcard = db.Text()   # vCard for CardDAV access; it's not a StringProperty
                      # because it might be longer than 500 characters

class PermissionEmail(db.Model):
    userGroup = db.ReferenceProperty(UserGroup,
                                     collection_name = "permissionEmails")
    emailAddress = db.ReferenceProperty(UserEmail,
                                        collection_name = "permissionEmails")
    canView = db.BooleanProperty(default = False)
    
#--------------------------------------------------
# Psinquing between users

class Psinque(db.Model):
    fromUser = db.ReferenceProperty(UserProfile,
                                    collection_name = "outgoing")
    toUser   = db.ReferenceProperty(UserProfile,
                                    collection_name = "incoming")
    status = db.StringProperty(choices = ["pending", "established", "rejected", "banned"])
    establishingTime = db.DateTimeProperty(auto_now = True)
  
class Contact(db.Model):
    displayName = db.StringProperty()
    establishingTime = db.DateTimeProperty(auto_now = True)
    incoming = db.ReferenceProperty(Psinque)
    outgoing = db.ReferenceProperty(Psinque)
    incomingType = db.IntegerProperty()  # 0 = none; 1 = public; 2 = private; 3 = pending authorization
    outgoingType = db.IntegerProperty()  # 0 = none; 2 = private; 3 = pending  (public are invisible)

class ContactGroup(db.Model):
    contact = db.ReferenceProperty(Contact,
                                   collection_name = "contactGroups")
    group = db.ReferenceProperty(UserGroup,
                                 collection_name = "contactGroups")

#--------------------------------------------------
# CardDAV passwords

class CardDAVPassword(db.Model):
    user = db.UserProperty()
    generatedUsername = db.StringProperty()
    generatedPassword = db.StringProperty()
