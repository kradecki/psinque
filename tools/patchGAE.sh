#!/bin/sh
cp tools/dev_appserver-allmethods ../google_appengine/google/appengine/tools
cd ../google_appengine/google/appengine/tools; patch -p1 < {dev_appserver-allmethods}