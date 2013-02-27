# -*- coding: utf-8 -*-

import logging

from wsgidav.wsgidav_app import WsgiDAVApp, DEFAULT_CONFIG
from carddav.Provider import CardDAVProvider
from carddav.DomainController import PsinqueDomainController
from google.appengine.ext.webapp.util import run_wsgi_app

def real_main():
    logging.debug("real_main")
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
    run_wsgi_app(app)


def profile_main():
    # This is the main function for profiling 
    # We've renamed our original main() above to real_main()
    import cProfile, pstats, StringIO
    prof = cProfile.Profile()
    prof = prof.runctx("real_main()", globals(), locals())
    stream = StringIO.StringIO()
    stats = pstats.Stats(prof, stream=stream)
    stats.sort_stats("time")  # Or cumulative
    stats.print_stats(80)  # 80 = how many to print
    # The rest is optional.
    # stats.print_callees()
    # stats.print_callers()
    logging.info("Profile data:\n%s", stream.getvalue())


#===============================================================================
# main()
# http://code.google.com/intl/en/appengine/docs/python/runtime.html#App_Caching
# "App caching provides a significant benefit in response time. 
#  We recommend that all applications use a main() routine, ..."
#===============================================================================
main = profile_main

if __name__ == "__main__":
    logging.debug("carddav.__main__")
    logging.getLogger().setLevel(logging.DEBUG)
    main()
