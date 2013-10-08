#!/bin/bash
# This needs to be run in the main project folder:
cd ..;python2.7 google_appengine/dev_appserver.py --enable_sendmail yes $* psinque
