
import os
import logging

os.environ['DJANGO_SETTINGS_MODULE'] = 'settings'

from google.appengine.api import users
from google.appengine.ext import webapp
from google.appengine.ext.webapp import template

from django.conf import settings
from django.utils import translation

from UserDataModels import UserSettings

class MenuEntry:
  url = ""
  title = ""
  entryclass = ""
  def __init__(self, url, title, entryclass = ""):
    self.url = url
    self.title = title
    self.entryclass = entryclass

class MasterHandler(webapp.RequestHandler):
  '''This is the base class for all handlers.'''
  '''It prepares all the information for the top bar.'''
    
  def sendTopTemplate(self, prettify = False, activeEntry = ""):
      
    menuentries = [
      MenuEntry("profile", translation.ugettext("Visiting card")),
      MenuEntry("notifications", translation.ugettext("Notifications")),
      MenuEntry("groups", translation.ugettext("Groups")),
      MenuEntry("contacts", translation.ugettext("Contacts")),
      MenuEntry("settings", translation.ugettext("Settings"))
    ]
    if activeEntry != "":
      activeEntry = translation.ugettext(activeEntry)
      for entry in menuentries:
        if entry.title == activeEntry:
           entry.entryclass = "active"
    
    if prettify:
        topTemplatePath = os.path.join(os.path.dirname(__file__), 'templates/topTemplate_Prettify.html')
    else:
        topTemplatePath = os.path.join(os.path.dirname(__file__), 'templates/topTemplate.html')
    self.response.out.write(translation.ugettext(template.render(topTemplatePath,
        dict(self.getUserVariables().items() + {'menuentries': menuentries}.items()
    ))))

  def sendBottomTemplate(self):
    bottomTemplatePath = os.path.join(os.path.dirname(__file__), 'templates/bottomTemplate.html')
    self.response.out.write(translation.ugettext(template.render(bottomTemplatePath, None)))

  def getUserVariables(self):
    user = users.get_current_user()
    if user:
        return {
          'username': user.nickname(),
          'loginurl': users.create_logout_url(self.request.uri),       
          'loginurl_linktext': translation.ugettext("Logout"),
          'settings': True
        }
    else:
        return {
          'username': "",
          'loginurl': users.create_login_url(self.request.uri),       
          'loginurl_linktext': translation.ugettext("Login"),
          'settings': False
        }

  def getLanguage(self):
    user = users.get_current_user()
    query = UserProfile.all()
    userProfile = query.filter("user =", user).get()
    if not userProfile:  # no user profile registered yet
      self.LANGUAGE_CODE = "en"
    else:
      self.LANGUAGE_CODE = userProfile.preferredLanguage
      logging.error("Changed language to " + settings.LANGUAGE_CODE)

  def activateTranslation(self, language = ""):
    translation.activate(language)
    if language == "":
      self.getLanguage()
    else:
      self.LANGUAGE_CODE = language
    translation.activate(self.LANGUAGE_CODE)

  def deactivateTranslation(self):
    translation.deactivate()

  def sendContent(self, templateName, templateVariables = None):
    path = os.path.join(os.path.dirname(__file__), templateName)
    self.response.out.write(translation.ugettext(template.render(path, templateVariables)))

  def render(self, activeEntry, templateName, templateVariables = None):
    MasterHandler.activateTranslation(self)
    MasterHandler.sendTopTemplate(self, activeEntry = activeEntry)
    MasterHandler.sendContent(self, templateName, templateVariables)
    MasterHandler.sendBottomTemplate(self)   
    MasterHandler.deactivateTranslation(self)

class StaticMasterHandler(MasterHandler):
  '''A simple class for handling static pages'''
  templateName = ""
  activeEntry  = ""
    
  def __init__(self, templateName, activeEntry = ""):
    self.templateName = templateName
    self.activeEntry  = activeEntry
    super(StaticMasterHandler, self).__init__()
    
  def get(self):
    MasterHandler.activateTranslation(self)
    self.sendTopTemplate(activeEntry = self.activeEntry)
    path = os.path.join(os.path.dirname(__file__), self.templateName)
    self.response.out.write(template.render(path, None))
    self.sendBottomTemplate()
    MasterHandler.deactivateTranslation(self)
