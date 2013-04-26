#!/bin/bash
# This needs to be run in the main project folder:
python2.7 ../google_appengine/dev_appserver.py --use_sql . $*
