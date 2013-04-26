#!/bin/bash
set -e

function checkTools {
  echo "Checking installed tools..."
  npm > /dev/null || ( echo "You need to have Node.js installed" && exit 1 )
  grunt -version > /dev/null || ( echo "You need grunt to compile jQuery" && exit 1)
}

function updateJQuery {
  echo "Updating jQuery..."
  cd jquery
  git pull    # update the repo
  npm install # install the jQuery dependencies
  grunt       # build jQuery
  cd ..
}

function updateWsgiDAV {
  echo "Updating WsgiDAV..."
  pwd
  cd wsgidav
  hg pull -u
  cd ..
}

checkTools
updateJQuery
# updateWsgiDAV
