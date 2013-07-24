#!/bin/bash
mkdir -p build
echo "Copying files to 'build'..."
cp *.py build/
cp app.yaml build/
cp index.yaml build/
cp -R stylesheets build/
cp -R templates build/
cp -R static build/
cp -R carddav build/
cp -R dateutil build/
cp -R wsgidav build/
echo "Minimizing java scripts..."
mkdir -p build/javascripts
for filename in javascripts/*.js; do
  echo " - $filename"
  uglifyjs $filename -m -c --screw-ie8 -o build/$filename
done
echo "Uploading the app..."
python2.7 ../google_appengine/appcfg.py update build
