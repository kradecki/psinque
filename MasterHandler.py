
import os

import jinja2
import logging
import webapp2

from google.appengine.api import users

from users.UserDataModels import UserSettings
from users.UserDataModels import UserProfile
from users.UserDataModels import Relationship

jinja_environment = jinja2.Environment(
    loader = jinja2.FileSystemLoader(os.path.dirname(__file__)))

class MenuEntry:
  url = ""
  title = ""
  entryclass = ""
  def __init__(self, url, title, entryclass = ""):
    self.url = url
    self.title = title
    self.entryclass = entryclass

class MasterHandler(webapp2.RequestHandler):
  '''
  This is the base class for all handlers.
  It prepares all data for the top menu bar.
  '''
    
  def sendTopTemplate(self, activeEntry = ""):

    user = users.get_current_user()
    if not user:  # user not logged in
      self.redirect("/login")
      return

    currentUserProfile = UserProfile.all().filter("user =", user).fetch(1, keys_only=True)[0]
    notificationCount = Relationship.all().filter("userTo =", currentUserProfile).filter("status =", "pending").count()
    if notificationCount > 0:
      self.notificationsText = "Notifications (" + str(notificationCount) + ")"
    else:
      self.notificationsText = "Notifications"

    menuentries = [
      MenuEntry("profile", "My card"),
      MenuEntry("notifications", self.notificationsText),
      MenuEntry("groups", "Groups"),
      MenuEntry("contacts", "Contacts"),
      MenuEntry("settings", "Settings")
    ]
    if activeEntry != "":
      for entry in menuentries:
        if entry.title == activeEntry:
           entry.entryclass = "active"  # mark menu item as active
    
    template = jinja_environment.get_template('templates/topTemplate.html')
    self.response.out.write(template.render(
      dict(self.getUserVariables().items() + {'menuentries': menuentries}.items()
    )))

  def sendBottomTemplate(self):
    template = jinja_environment.get_template('templates/bottomTemplate.html')
    self.response.out.write(template.render())

  def getUserVariables(self):
    user = users.get_current_user()
    if user:
        return {
          'username': user.nickname(),
          'loginurl': users.create_logout_url(self.request.uri),       
          'loginurl_linktext': "Logout",
          'settings': True
        }
    else:
        raise Exception("User not logged in.")   # this should never happen, because sendTopTemplate() redirects to /login earlier

  def getLanguage(self):
    user = users.get_current_user()
    query = UserSettings.all()
    userProfile = query.filter("user =", user).get()
    if not userProfile:  # no user profile registered yet
      self.LANGUAGE_CODE = "en"
    else:
      self.LANGUAGE_CODE = userProfile.preferredLanguage
      logging.error("Changed language to " + settings.LANGUAGE_CODE)

  def sendContent(self, templateName, templateVariables = None):
    template = jinja_environment.get_template(templateName)
    self.response.out.write(template.render(templateVariables))

  def render(self, activeEntry, templateName, templateVariables = None):
    self.sendTopTemplate(activeEntry = activeEntry)
    self.sendContent(templateName, templateVariables)
    self.sendBottomTemplate()

class StaticMasterHandler(MasterHandler):
  '''
  A simple class for handling static pages.
  '''
  templateName = ""
  activeEntry  = ""
  
  def __init__(self, templateName, activeEntry = ""):
    self.templateName = templateName
    self.activeEntry  = activeEntry
    super(StaticMasterHandler, self).__init__()
    
  def get(self):
    self.sendTopTemplate(activeEntry = self.activeEntry)
    template = jinja_environment.get_template(self.templateName)
    self.response.out.write(template.render(None))
    self.sendBottomTemplate()
