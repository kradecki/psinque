
from google.appengine.ext import db

availableLanguages = ["en", "pl", "dk"]

class UserSettings(db.Model):
  '''User settings other than those stored in the profile'''
  user = db.UserProperty()
 
  # Settings:
  preferredLanguage = db.StringProperty(choices = availableLanguages)

class UserProfile(db.Model):
  '''User profile'''
  user = db.UserProperty()

  lastname = db.StringProperty()
  firstname = db.StringProperty()
  middlename = db.StringProperty()

  # ...
