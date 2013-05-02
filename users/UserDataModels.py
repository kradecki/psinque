
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
  notifyOnNewsletter = db.BooleanProperty(default = False)   # I _never_ ask for newsletters, so why force it on the users?
  
  cardDAVenabled = db.BooleanProperty(default = True)  #TODO: Disable this after testing

#--------------------------------------------------
# User profile

genders    = ["male", "female"]
phoneTypes = ["home landline", "private cellphone", "work cellphone", "work landline", "home fax", "work fax", "other"]

class UserProfile(db.Model):
  '''User profile'''
  user = db.UserProperty()

  photograph = blobstore.BlobReferenceProperty()

  firstname = db.StringProperty(required = True,
                                default = "Jan")
  middlename = db.StringProperty(required = False)
  lastname = db.StringProperty(required = True,
                               default = "Kowalski")
  pseudonym = db.StringProperty(required = False)

  gender = db.StringProperty(choices = genders,
                             required = False)

  birthDay = db.DateProperty()  
  
  # nationality? namesday?

addressTypes = {'home': 'Home', 'work': 'Work'}

class UserAddress(db.Model):
  user = db.ReferenceProperty(UserProfile,
                              collection_name="addresses")
  address = db.PostalAddressProperty()
  city = db.StringProperty()
  postalCode = db.StringProperty()
  addressType = db.StringProperty(choices = addressTypes.keys())
  location = db.GeoPtProperty()

class UserEmail(db.Model):
  user = db.ReferenceProperty(UserProfile)
  email = db.EmailProperty()
  emailType = db.StringProperty(choices = ["home", "work"])

class UserIM(db.Model):
  user = db.ReferenceProperty(UserProfile)
  im = db.IMProperty()

class UserPhoneNumber(db.Model):
  user = db.ReferenceProperty(UserProfile, collection_name="phoneNumbers")
  phone = db.PhoneNumberProperty(required = True)
  phoneType = db.StringProperty(choices = phoneTypes)

class UserWebpage(db.Model):
  user = db.ReferenceProperty(UserProfile)
  address = db.StringProperty()
  webpageType = db.StringProperty(choices = ["private homepage", "business homepage", "facebook", "myspace", "other"])

#--------------------------------------------------
# Groups of users

class UserGroups(db.Model):
  creator = db.ReferenceProperty(UserProfile)
  groupName = db.StringProperty()
  canViewHomeData = db.BooleanProperty()
  canViewWorkData = db.BooleanProperty()
  canViewBothData = db.BooleanProperty()
  vcard = db.Text()   # vCard for CardDAV access; it's not a StringProperty
                      # because it might be longer than 500 characters
  
#--------------------------------------------------
# Relationships between users

class Relationship(db.Model):
  userFrom = db.ReferenceProperty(UserProfile, collection_name = "outgoingRelationships")
  userTo = db.ReferenceProperty(UserProfile, collection_name = "ingoingRelationships")
  status = db.StringProperty(choices = ["pending", "established", "rejected", "banned"])
  establishingTime = db.DateTimeProperty()
  group = db.ReferenceProperty(UserGroups, collection_name = "relationships")

#--------------------------------------------------
# CardDAV passwords

class CardDAVPassword(db.Model):
    user = db.UserProperty()
    generatedUsername = db.StringProperty()
    generatedPassword = db.StringProperty()
