# -*- coding: utf-8 -*-

import logging

from wsgidav.wsgidav_app import WsgiDAVApp, DEFAULT_CONFIG
import wsgidav.util

from carddav.Provider import CardDAVProvider, WellKnownProvider
from carddav.DomainController import PsinqueDomainController

from DataModels import Contact, Group, CardDAVLogin
from DataManipulation import reallyGenerateVCard

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

    group = Group.all(). \
                  ancestor(userProfile). \
                  filter("name =", groupName). \
                  get()
    
    contacts = Contact.all(). \
                       ancestor(userProfile). \
                       filter("group =", group)
    
    for contact in contacts:
        friendList.append(str(contact.key()) + ".vcf")
        
    return friendList


def getVCard(contactID):
    
    # This is 3 Datastore fetches: Contact, Psinque, Persona
    logging.info("Getting vCard for Contact " + contactID)
    contact = Contact.get(contactID)
    persona = contact.incoming.persona
    if persona.vcardNeedsUpdating:
        reallyGenerateVCard(persona)
    return [persona.vcard, persona.vcardMTime, persona.vcardMD5]


def getCardDAVLogin(username):

    carddavLogin = CardDAVLogin.all(). \
                                filter("generatedUsername =", username). \
                                get()
    if not carddavLogin:
        return None
    
    if not carddavLogin.parent().userSettings.cardDAVenabled:
        return None
      
    carddavLogin.put()  # to update the 'lastUsed' field

    return carddavLogin


def getUserProfile(username):
    
    carddavLogin = getCardDAVLogin(username)
    
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
    "acceptbasic": True,      
    "acceptdigest": False,
    "defaultdigest": False,    
    "domaincontroller": domainController,
    "dir_browser": {
        "enable": False,
       },
    "enable_loggers": ["property_manager"],
    })

app = WsgiDAVApp(config)
