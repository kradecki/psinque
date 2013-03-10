# -*- coding: utf-8 -*-

import logging

from wsgidav.wsgidav_app import WsgiDAVApp, DEFAULT_CONFIG
import wsgidav.util

from carddav.Provider import CardDAVProvider, WellKnownProvider
from carddav.DomainController import PsinqueDomainController

provider = CardDAVProvider()
wellknowns = WellKnownProvider()
domainController = PsinqueDomainController()

logging.info("Starting CardDAVProvider")

config = DEFAULT_CONFIG.copy()
config.update({
    "provider_mapping": {"/carddav/": provider,         # RFC 6352
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
