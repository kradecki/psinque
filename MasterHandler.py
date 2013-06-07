# -*- coding: utf-8 -*-

import os
from datetime import datetime
import dateutil.relativedelta

import jinja2
import logging
import webapp2

from google.appengine.api import users

from django.utils import simplejson as json

from DataModels import UserSettings, UserProfile, Psinque

#-----------------------------------------------------------------------------

jinja_environment = jinja2.Environment(
    loader = jinja2.FileSystemLoader(os.path.dirname(__file__))
)

# Custom filter for jinja2 to display date in a human-readable form
def humanizeDateTime(value):
    
    timeDifference = dateutil.relativedelta.relativedelta(datetime.now(), value)
    
    attrs = [u'years', u'months', u'days', u'hours', u'minutes', u'seconds']
    human_readable = lambda delta: ['%d %s' % (getattr(delta, attr), getattr(delta, attr) > 1 and attr or attr[:-1]) for attr in attrs if getattr(delta, attr)]
    
    readableDifference = human_readable(timeDifference)
    
    if len(readableDifference) == 0:
        return u"Just now"
    
    readableDifference = readableDifference[0] + u" ago"
    if u'seconds' in readableDifference:
        return u"Less than a minute ago"
    if u'minutes' in readableDifference and timeDifference.minutes < 10:
        return u"Few minutes ago"

    return readableDifference

jinja_environment.filters['humanizeddatetime'] = humanizeDateTime

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
    The base class for all Psinque request handlers.
    '''

    def get(self, actionName):

        if self.safeGuard():
            
            try:
                actionFunction = getattr(self, actionName)
                logging.info("MasterHandler: Found action method.")
            except AttributeError as e:
                logging.error("MasterHandler: Action method not found.")
                logging.error(e)
                self.error404()
                return

            try:
                actionFunction()
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
        '''
        Retrieves the UserProfile for the current user from the Datastore.
        If the profile does not exist, the user is redirected to the profile
        edit page.
        '''        
        if self.safeGuard():
            self.userProfile = UserProfile.all(keys_only = True).filter("user =", self.user).get()
            if not self.userProfile:
                self.redirect("/mycard/view")
                return False
            self.userProfile = UserProfile.get(self.userProfile)  # retrieve actual data from datastore
            return True
        else:
            return False


    def getRequiredParameter(self, parameterName):
        '''
        Retrieves a text parameter from the HTTP request and raises an
        error if the parameter is not found.
        '''
        val = self.request.get(parameterName)
        if val == "":
            raise AjaxError("Parameter " + parameterName + " should not be empty.")
        return val
        
        
    def getRequiredBoolParameter(self, name):
        '''
        Retrieves a Boolean parameter from the HTTP request and raises an 
        error if the parameter is not found.
        '''
        try:
            val = self.getRequiredParameter(name)
            val = {"true": True, "false": False}[val]
            return val
        except KeyError:
            raise AjaxError("Unknown permission value: " + val);
    
        
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
            MenuEntry("mycard/view", "My card"),
            MenuEntry("permits/view", "Permits"),
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


    #def getLanguage(self):
        
        #query = UserSettings.all()
        #userProfile = query.filter("user =", self.user).get()
        #if not userProfile:  # no user profile registered yet
            #self.LANGUAGE_CODE = "en"
        #else:
            #self.LANGUAGE_CODE = userProfile.preferredLanguage
            #logging.error("Changed language to " + settings.LANGUAGE_CODE)


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
