
import os
import logging
import urllib

from google.appengine.api import users
from google.appengine.ext import blobstore
from google.appengine.ext import webapp
from google.appengine.ext.webapp import blobstore_handlers
from google.appengine.ext.webapp import template
from google.appengine.ext.webapp.util import run_wsgi_app

from MasterHandler import MasterHandler
from UserDataModels import UserProfile, UserSettings, availableLanguages

class ViewProfile(MasterHandler):

  def get(self):
    user = users.get_current_user()
    query = UserProfile.all()
    userProfile = query.filter("user =", user).get()
    if not userProfile:  # no user profile registered yet, so ask user to create his profile
      self.redirect("/editprofile")  # and redirect to edit the profile
      return

    template_values = {
      'firstname': userProfile.firstname,
      'lastname': userProfile.lastname,
      'photograph': None
    }
    if userProfile.photograph != None:
      template_values['photograph'] = '/serveimageblob/%s' % userProfile.photograph.key()
    
    MasterHandler.sendTopTemplate(self, activeEntry = "My card")
    MasterHandler.sendContent(self, 'templates/viewProfile.html', template_values)
    MasterHandler.sendBottomTemplate(self)

class EditProfile(MasterHandler):

  def get(self):   # form for editing details
    user = users.get_current_user()
    query = UserProfile.all()
    userProfile = query.filter("user =", user).get()
    if not userProfile:  # no user profile registered yet, so create a new one
      userProfile = UserProfile()
      userProfile.user = user
      userProfile.put()  # save the new (and empty) profile in the Datastore
      userSettings = UserSettings()
      userSettings.user = user
      userSettings.put()
      logging.error(availableLanguages.keys())
      firstLogin = True
    else:
      firstLogin = False

    MasterHandler.sendTopTemplate(self, activeEntry = "My card")
    MasterHandler.sendContent(self, 'templates/editProfile.html', {
      'firstlogin': firstLogin,
      'firstname': userProfile.firstname,
      'lastname': userProfile.lastname,
      })
    MasterHandler.sendBottomTemplate(self)

  def post(self):  # executed when the user hits the 'Save' button, which sends a POST request
    user = users.get_current_user()
    query = UserProfile.all()
    userProfile = query.filter("user =", user).get()
    userProfile.firstname = self.request.get('firstname')
    userProfile.lastname = self.request.get('lastname')
    userProfile.put()

    self.redirect('/profile')  # redirects to ViewProfile

class UploadPhoto(MasterHandler):
  def get(self):
    MasterHandler.sendTopTemplate(self, activeEntry = "My card")
    MasterHandler.sendContent(self, 'templates/uploadProfilePhoto.html', {
      'photoUploadLink': blobstore.create_upload_url('/uploadphotopost'),
      })
    MasterHandler.sendBottomTemplate(self)

class UploadHandler(blobstore_handlers.BlobstoreUploadHandler):
  def post(self):
    upload_files = self.get_uploads('file')  # 'file' is file upload field in the form
    blob_info = upload_files[0]
    user = users.get_current_user()
    userProfile = UserProfile.all().filter("user =", user).get()
    userProfile.photograph = blob_info.key()
    userProfile.put()
    self.redirect('/profile')  # go back to the profile viewer

class ServeHandler(blobstore_handlers.BlobstoreDownloadHandler):
  def get(self, resource):
    resource = str(urllib.unquote(resource))
    logging.info("Getting a blob " + resource)
    blob_info = blobstore.BlobInfo.get(resource)
    self.send_blob(blob_info)

application = webapp.WSGIApplication([
  ('/profile', ViewProfile),
  ('/editprofile', EditProfile),
  ('/submitprofile', EditProfile),
  ('/uploadphoto', UploadPhoto),
  ('/uploadphotopost', UploadHandler),
  ('/serveimageblob/([^/]+)?', ServeHandler),
], debug=True)

def main():
  run_wsgi_app(application)

if __name__ == '__main__':
  main()
