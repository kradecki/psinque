# -*- coding: utf-8 -*-

import logging

from wsgidav.wsgidav_app import WsgiDAVApp, DEFAULT_CONFIG
import wsgidav.util

from carddav.Provider import CardDAVProvider, WellKnownProvider
from carddav.DomainController import PsinqueDomainController

from Psinque import Contact, Group

#-----------------------------------------------------------------------------

class CardDAVLogin(db.Model):

    name = db.StringProperty()
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
    
    # This is 3 Datastore fetches: Contact, Psinque, Permit
    permit = Contact.get_by_id(friendID).incoming.permit
    return [permit.vcard, permit.vcarsMTime, permit.vcardMD5]


def getCardDAVLogin(username):

    carddavLogin = CardDAVPassword.all().
                                   filter("generatedUsername =", username).
                                   get()
    if not carddavLogin:
        return None
    
    if not carddavLogin.parent().userSettings.cardDAVenabled:
        return None

    return carddavLogin


def getUserProfile(username):
    
    carddavLogin = getCardDAVLogin()
    
    return carddavLogin.parent()

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
