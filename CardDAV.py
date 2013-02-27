# -*- coding: utf-8 -*-

import logging

from wsgidav.wsgidav_app import WsgiDAVApp, DEFAULT_CONFIG

from carddav.Provider import CardDAVProvider
from carddav.DomainController import PsinqueDomainController

provider = CardDAVProvider()
domainController = PsinqueDomainController()

config = DEFAULT_CONFIG.copy()
config.update({
    "provider_mapping": {"/carddav/": provider},
    "verbose": 2,
    "enable_loggers": [],
    "propsmanager": False,                    
    "locksmanager": False,

    # Use Basic Authentication and don't fall back to Digest Authentication,
    # because our domain controller doesn't have no access to the user's 
    # passwords.
    "acceptbasic": False,      
    "acceptdigest": True,
    "defaultdigest": True,    
    "domaincontroller": domainController,
    "dir_browser": {
        "enable": False,
        },
    })

app = WsgiDAVApp(config)
