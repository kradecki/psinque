
from google.appengine.ext import db

availableLanguages = ["en", "pl", "dk"]

class UserSettings(db.Model):
  '''User settings other than those stored in the profile'''
  user = db.UserProperty()
 
  # Settings:
  preferredLanguage = db.StringProperty(choices = availableLanguages)
  notifyOnNewsletter = db.BooleanProperty()

class UserProfile(db.Model):
  '''User profile'''
  user = db.UserProperty()

  lastname = db.StringProperty()
  firstname = db.StringProperty()
  middlename = db.StringProperty()

  gender = db.StringProperty(choices = ["male", "female"])

  birthDay = db.DateProperty()  

  # nationality? namesday?
  
class UserAddress(db.Model):
  user = db.ReferenceProperty(UserProfile)   # or perhaps db.UserProperty()
  address = db.PostalAddressProperty()
  addressType = db.StringProperty(choices = ["home", "work"])

class UserEmail(db.Model):
  user = db.ReferenceProperty(UserProfile)
  email = db.EmailProperty()
  emailType = db.StringProperty(choices = ["home", "work"])

class UserIM(db.Model):
  user = db.ReferenceProperty(UserProfile)
  im = db.IMProperty()

class UserPhoneNumber(db.Model):
  user = db.ReferenceProperty(UserProfile)
  phone = db.PhoneNumberProperty()
  phoneType = db.StringProperty(choices = ["home landline", "private cellphone", "work cellphone", "work landline", "other"])

class UserWebpage(db.Model):
  user = db.ReferenceProperty(UserProfile)
  address = db.StringProperty()
  webpageType = db.StringProperty(choices = ["private homepage", "business homepage", "facebook", "myspace", "other"])

class UserGroups(db.Model):
  creator = db.ReferenceProperty(UserProfile)
  groupName = db.StringProperty()
  canViewHomeData = db.BooleanProperty()
  canViewWorkData = db.BooleanProperty()
  canViewBorthDate = db.BooleanProperty()
  # Every friend can see the names and the gender
  
class Relationship(db.Model):
 user1 = db.ReferenceProperty(UserProfile)
 #user2 = db.ReferenceProperty(UserProfile)
 status = db.StringProperty(choices = ["pending", "established"])
 establishingTime = db.DateTimeProperty()
