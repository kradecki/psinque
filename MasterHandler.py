
import os

import jinja2
import logging
import webapp2

from google.appengine.api import users

from django.utils import simplejson as json

from users.UserDataModels import UserSettings
from users.UserDataModels import UserProfile
from users.UserDataModels import Psinque

jinja_environment = jinja2.Environment(
    loader = jinja2.FileSystemLoader(os.path.dirname(__file__)))

#-----------------------------------------------------------------------------

class MenuEntry:
    url = ""
    title = ""
    entryclass = ""
    def __init__(self, url, title, entryclass = ""):
        self.url = url
        self.title = title
        self.entryclass = entryclass

#-----------------------------------------------------------------------------

class AjaxError(Exception):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)

#-----------------------------------------------------------------------------

class MasterHandler(webapp2.RequestHandler):
    '''
    This is the base class for all Psinque handlers.
    '''

    def get(self, actionName):
        
        if self.safeGuard():
            
            try:
                actionFunction = getattr(self, actionName)
                actionFunction()
            except AttributeError:
                self.error404()
            except AjaxError as e:
                self.sendJsonError(e.value)
  
    def safeGuard(self):
        '''
        Checks if a user is logged in and if not, redirects
        to the login page.
        '''
        self.user = users.get_current_user()
        if not self.user:  # user not logged in
            self.redirect("/login")
            return False
        return True
    
    
    def getUserProfile(self):
        
        if self.safeGuard():
            self.userProfile = UserProfile.all(keys_only = True).filter("user =", self.user).get()
            if not self.userProfile:
                self.redirect("/mycard/edit")
                return False
            self.userProfile = UserProfile.get(self.userProfile)  # retrieve actual data from datastore
            return True
        else:
            return False


    def checkGetParameter(self, parameterName):
        
        val = self.request.get(parameterName)
        if val == "":
            raise AjaxError("Parameter " + parameterName + " should not be empty.")
        return val
        
        
    def sendJsonOK(self, additionalValues = {}):
        
        self.response.out.write(json.dumps(dict({"status": 0}.items() +
                                                additionalValues.items())))


    def sendJsonError(self, msg):
        
        self.response.out.write(json.dumps({"status": 1,
                                            "message": msg}))


    def sendTopTemplate(self, activeEntry = ""):
        
        user = users.get_current_user()
        currentUserProfile = UserProfile.all().filter("user =", user).fetch(1, keys_only=True)[0]
        notificationCount = Psinque.all().filter("userTo =", currentUserProfile).filter("status =", "pending").count()
        if notificationCount > 0:
            self.psinqueText = "Psinques (" + str(notificationCount) + ")"
        else:
            self.psinqueText = "Psinques"

        menuentries = [
            MenuEntry("mycard/edit", "My card"),
            MenuEntry("groups/view", "Groups"),
            MenuEntry("psinques/view", self.psinqueText),
            MenuEntry("settings/view", "Settings")
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
        
        query = UserSettings.all()
        userProfile = query.filter("user =", self.user).get()
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
        
        
    def error404(self):
        
        self.error(404)
        template = jinja_environment.get_template('templates/notFound.html')
        self.response.out.write(template.render(requestName = self.request.uri))

#-----------------------------------------------------------------------------

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
        MasterHandler.safeGuard()
        MasterHandler.sendTopTemplate(activeEntry = self.activeEntry)
        template = jinja_environment.get_template(self.templateName)
        self.response.out.write(template.render(None))
        MasterHandler.sendBottomTemplate()
