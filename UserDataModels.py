
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
  
class UserAddress(db.Model):
  user = db.ReferenceProperty(UserProfile,       # or perhaps db.UserProperty()
                              collection_name="addresses")
  address = db.PostalAddressProperty()
  addressType = db.StringProperty(choices = ["home", "work"])
  primary = db.BooleanProperty()
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
  canViewBorthDate = db.BooleanProperty()
  # Every friend can see the names and the gender
  
#--------------------------------------------------
# Relationships between users

class Relationship(db.Model):
 user1 = db.ReferenceProperty(UserProfile, collection_name="outgoingRelationships")
 user2 = db.ReferenceProperty(UserProfile, collection_name="ingoingRelationships")
 status = db.StringProperty(choices = ["pending", "established"])
 establishingTime = db.DateTimeProperty()
