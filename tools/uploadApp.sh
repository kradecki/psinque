#!/bin/bash
mkdir -p build
echo "Copying files to 'build'..."
cp *.py build/
cp app.yaml build/
cp index.yaml build/
cp -R static build/
cp -R carddav build/
cp -R dateutil build/
cp -R wsgidav build/
echo "Minimizing java scripts..."
mkdir -p build/javascripts
for filename in javascripts/*.js; do
  echo " - $filename"
  uglifyjs $filename -m -c --screw-ie8 > build/$filename
done
echo "Minimizing stylesheets..."
mkdir -p build/javascripts
for filename in stylesheets/*.css; do
  echo " - $filename"
  yuicompressor $filename -o build/$filename
done
echo "Minimizing templates..."
mkdir -p build/templates
for filename in templates/*.html; do
  echo " - $filename"
  cat $filename | sed -e 's/^ *//g' | sed -e ':a;N;$!ba;s/>\n</></g' > build/$filename
done
echo "Uploading the app..."
python2.7 ../google_appengine/appcfg.py update build
