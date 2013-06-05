# -*- coding: utf-8 -*-

import logging

from wsgidav.wsgidav_app import WsgiDAVApp, DEFAULT_CONFIG
import wsgidav.util

from carddav.Provider import CardDAVProvider, WellKnownProvider
from carddav.DomainController import PsinqueDomainController

from Psinque import Contact, Group

#-----------------------------------------------------------------------------

class CardDAVPassword(db.Model):

    generatedUsername = db.StringProperty()
    generatedPassword = db.StringProperty()

#-----------------------------------------------------------------------------

def groupList(userProfile):
    """Returns the list of all groups created by the logged in user.

    :returns: list -- the list of groups

    """
    groupNames = []
    for group in Group.all().ancestor(userProfile):
        if group.sync:
            groupNames.append(group.name)       
    return groupNames


def friendList(userProfile, groupName):
    
    friendList = []

    group = Group.all().ancestor(userProfile).filter("name =", groupName).get()
    for contact in Contact.all().ancestor(userProfile).filter("group =", group):
        friendList.append(contact.id())
        
    return friendList


def getVCard(friendID):
    
    return Contact.get_by_id(friendID).group.vCard


#TODO: Set up generated password indexes
def cardDAVPassword(username):
    
    password = CardDAVPassword.all().filter("generatedUsername =", username).get()
    if not password:  # no user profile registered yet
        return None

    if not getUserSettings(password.user).cardDAVenabled: # this can happen if the user's disabled CardDAV, but somehow the passwords is still here
        password.delete()
        return False

    return password.generatedPassword


def cardDAVUser(username):
    
    password = CardDAVPassword.all().filter("generatedUsername =", username).get()
    if not password:
        return None
    return password.user

#-----------------------------------------------------------------------------

provider = CardDAVProvider()
wellknowns = WellKnownProvider()
domainController = PsinqueDomainController()

logging.info("Starting CardDAVProvider")

config = DEFAULT_CONFIG.copy()
config.update({
    "provider_mapping": {"/carddav/": provider,        # RFC 6352
                         "/.well-known/": wellknowns,   # RFC 5785
                        },
    "verbose": 1,
    "enable_loggers": [],
    "propsmanager": False,                    
    "locksmanager": False,
    "acceptbasic": False,      
    "acceptdigest": True,
    "defaultdigest": True,    
    "domaincontroller": domainController,
    "dir_browser": {
        "enable": False,
       },
    "enable_loggers": ["property_manager"],
    })

app = WsgiDAVApp(config)
