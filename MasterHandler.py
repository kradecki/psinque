# -*- coding: utf-8 -*-

import os
from datetime import datetime
import dateutil.relativedelta

import jinja2
import logging
import webapp2

from google.appengine.api import users

from django.utils import simplejson as json

from DataModels import UserSettings, UserProfile, Psinque, Invitation

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

        self.user = users.get_current_user()

        if (not "view" in actionName) and (not self.getUserProfile()):
            #self.sendJsonError("User profile not found")
            return
                    
        try:
            actionFunction = getattr(self, actionName)
        except AttributeError as e:
            logging.error("Action method not found:")
            logging.error(e)
            self.error404()
            return

        try:
            actionFunction()
        except AjaxError as e:
            logging.error("AjaxError:")
            logging.error(e)
            self.sendJsonError(e.value)
                
    
    def getUserProfile(self):
        '''
        Retrieves the UserProfile for the current user from the Datastore.
        If the profile does not exist, the user is redirected to the profile
        edit page.
        '''
        try:
            getattr(self, "userProfile")
            return True
        except AttributeError:
            self.userProfile = UserProfile.all(keys_only = True).filter("user =", self.user).get()
            if not self.userProfile:
                self.redirect("/profile/view")
                return False
            self.userProfile = UserProfile.get(self.userProfile)  # retrieve actual data from datastore
            return True


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
            raise AjaxError("Unknown Boolean value: " + val);
    
        
    def sendJsonOK(self, additionalValues = {}):
        
        self.response.headers['Content-Type'] = "application/json"
        self.response.out.write(json.dumps(dict({"status": 0}.items() +
                                                additionalValues.items())))


    def sendJsonError(self, msg):
        
        self.response.headers['Content-Type'] = "application/json"
        self.response.out.write(json.dumps({"status": 1,
                                            "message": msg}))


    def sendContent(self, templateName,
                    activeEntry = "",
                    templateVariables = None):
        
        if self.user:
            try:
                getattr(self, "userProfile")
            except AttributeError:
                if not self.getUserProfile():
                    return

            if not self.userProfile.active:
              
                email = self.userProfile.emails.get().itemValue
                invitation = Invitation.all().filter("email =", email).get()
                if not invitation is None:
                    invitation.status = "used"
                    invitation.put()
                    self.userProfile.active = True
                    self.userProfile.put()
                else:
                    self.restrictedAccess()
                    return

            notificationCount = Psinque.all(keys_only = True). \
                                        filter("fromUser =", self.userProfile). \
                                        filter("status =", "pending"). \
                                        count()

            menuentries = [
                MenuEntry("profile/view", "Profile"),
                MenuEntry("personas/view", "Personas"),
                MenuEntry("psinques/view", "Psinques"),
                MenuEntry("settings/view", "Settings"),
            ]
            if activeEntry != "":
                for entry in menuentries:
                    if entry.title == activeEntry:
                        entry.entryclass = "active"  # mark menu item as active

            if templateVariables:
                allTemplateVariables = dict(templateVariables.items() +
                    self.getUserVariables().items() + {
                        'menuentries': menuentries,
                        'notificationCount': notificationCount
                    }.items())
            else:
                allTemplateVariables = dict(self.getUserVariables().items() +
                    {'menuentries': menuentries}.items())
                
        else:
            allTemplateVariables = templateVariables

        template = jinja_environment.get_template(templateName)
        self.response.out.write(template.render(allTemplateVariables))


    def displayMessage(self, templateName, templateVariables = None):

        template = jinja_environment.get_template(templateName)
        self.response.out.write(template.render(allTemplateVariables))


    def restrictedAccess(self):
      
        template = jinja_environment.get_template('templates/Message_restricted.html')
        self.response.out.write(template.render())


    def getUserVariables(self):
        
        user = users.get_current_user()
        if user:
            return {
                'username': user.nickname(),
                'logouturl': users.create_logout_url(self.request.uri),       
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
        
        
    def error404(self):
        
        self.error(404)
        template = jinja_environment.get_template('templates/notFound.html')
        self.response.out.write(template.render(requestName = self.request.uri))


#-----------------------------------------------------------------------------

class StaticHandler(webapp2.RequestHandler):
    '''
    The base class for all static Psinque request handlers.
    '''

    def get(self, actionName):

        try:
            actionFunction = getattr(self, actionName)
        except AttributeError as e:
            logging.error("Action method not found:")
            logging.error(e)
            self.error404()
            return

        actionFunction()


    def sendContent(self, templateName, templateVariables = {}):
        
        template = jinja_environment.get_template(templateName)
        self.response.out.write(template.render(templateVariables))
        
        
    def error404(self):
        
        self.error(404)
        template = jinja_environment.get_template('templates/notFound.html')
        self.response.out.write(template.render(requestName = self.request.uri))

