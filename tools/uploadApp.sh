#!/bin/bash
mkdir -p build
echo "Copying files to 'build'..."
cp *.py build/
cp *.yaml build/
cp -R stylesheets build/
cp -R templates build/
cp -R static build/
echo "Minimizing java scripts..."
mkdir -p build/javascripts
for filename in javascripts/*.js; do
  uglifyjs -mt $filename > build/$filename
done
echo "Uploading the app..."
# python2.7 ../google_appengine/appcfg.py update .
