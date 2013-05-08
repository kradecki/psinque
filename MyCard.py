
import os
import logging
import urllib
import webapp2

from google.appengine.ext import db
from google.appengine.api import users
from google.appengine.ext import blobstore
from google.appengine.ext.webapp import blobstore_handlers

from MasterHandler import MasterHandler
from users.UserDataModels import UserProfile, UserSettings, UserAddress, UserEmail
from users.UserDataModels import UserGroup, CardDAVPassword

# Available data type choices:
from users.UserDataModels import availableLanguages, addressTypes, emailTypes

#-----------------------------------------------------------------------------

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
            'photograph': None,
            'emails': userProfile.emails,
            'addresses': userProfile.addresses,
            }
        #if userProfile.photograph != None:
            #template_values['photograph'] = '/serveimageblob/%s' % userProfile.photograph.key()
                
        MasterHandler.sendTopTemplate(self, activeEntry = "My card")
        MasterHandler.sendContent(self, 'templates/myCard_viewProfile.html', template_values)
        MasterHandler.sendBottomTemplate(self)
            
#-----------------------------------------------------------------------------

class EditProfile(MasterHandler):

    def get(self):   # form for editing details

        MasterHandler.safeGuard(self)
        userProfile = UserProfile.all().filter("user =", self.user).get()
        
        firstLogin = (not userProfile)        
        if firstLogin:  # no user profile registered yet, so create a new one
        
            userProfile = UserProfile(user = self.user)
            userProfile.put()  # save the new (and empty) profile in the Datastore
            
            userSettings = UserSettings(parent = userProfile, user = self.user)
            userSettings.put()
            
            cardDAVPassword = CardDAVPassword(parent = userSettings,
                                              user = self.user,
                                              generatedUsername = 'dupa',
                                              generatedPassword = 'dupa')
            cardDAVPassword.put()
            
            publicGroup = UserGroup(parent = userProfile, creator = userProfile,
                                    name = 'Public')
            publicGroup.put()
        
        userAddresses = userProfile.addresses.ancestor(userProfile).fetch(100)
        addresses = map(lambda x: {'nr': str(x+1), 'value': userAddresses[x]}, range(0, len(userAddresses)))
        if len(addresses) == 0:
            addresses = [{'nr': 1, 'value': None}]
            
        userEmails = userProfile.emails.ancestor(userProfile).fetch(100)
        if len(userEmails) == 0:
            userEmails = [{'address': '', 'primary': True, 'emailType': 'private'}]
                
        template_values = {
            'firstlogin': firstLogin,
            'firstname': userProfile.firstname,
            'lastname': userProfile.lastname,
            'emails': userEmails,
            'addresses': addresses,
            'emailTypes': emailTypes,
            'addressTypes': addressTypes,
            }
            
        MasterHandler.sendTopTemplate(self, activeEntry = "My card")
        MasterHandler.sendContent(self, 'templates/myCard_editProfile.html', template_values)
        MasterHandler.sendBottomTemplate(self)


    #TODO:Add transactions to profile updates
    def post(self):  # executed when the user hits the 'Save' button, which sends a POST request
    
        MasterHandler.safeGuard(self)
        userProfile = UserProfile.all().filter("user =", self.user).fetch(1)[0]
        
        # We start by removing all currently stored data
        # that is kept in separate entities,
        # so that they're not doubled in the datastore.
        # This is because it's impossible to tell which
        # of the new entities correspond to the old ones.
        for address in userProfile.addresses:
            address.delete()
        for email in userProfile.emails: # same for emails
            email.delete()
            
        for argumentName in self.request.arguments():
            
            if argumentName == 'firstname':
                userProfile.firstname = self.request.get(argumentName)
                
            elif argumentName == 'lastname':
                userProfile.lastname = self.request.get(argumentName)
                
            elif argumentName == 'middlename':
                userProfile.middlename = self.request.get(argumentName)
                
            elif argumentName == 'pseudonym':
                userProfile.pseudonym = self.request.get(argumentName)
                
            elif argumentName.startswith("address") and (self.request.get(argumentName) != ''):
                addressNumber = argumentName.replace("address", "")
                newUserAddress = UserAddress(parent = userProfile, user = userProfile,
                                             address = self.request.get(argumentName),
                                             city = self.request.get("city" + addressNumber),
                                             postalCode = self.request.get("postal" + addressNumber),
                                             addressType = self.request.get("typeofAddress" + addressNumber))
                lat = self.request.get("lat" + addressNumber)
                lon = self.request.get("long" + addressNumber)
                if lat != "" and lon != "":
                    newUserAddress.location = db.GeoPt(lat = lat, lon = lon)
                else:
                    newUserAddress.location = None
                newUserAddress.put()
                
            elif argumentName.startswith("email") and (self.request.get(argumentName) != ''):
                emailNumber = argumentName.replace("email", "")
                newEmail = UserEmail(parent = userProfile,
                                     user = userProfile,
                                     email = self.request.get(argumentName),
                                     emailType = self.request.get("typeofEmail" + emailNumber),
                                     primary = (emailNumber == '1'))
                newEmail.put()
        
        userProfile.put()  # update the user profile
                
        self.redirect('/profile')  # redirects to ViewProfile

#-----------------------------------------------------------------------------
                                                
class UploadPhoto(MasterHandler):
    def get(self):
        MasterHandler.sendTopTemplate(self, activeEntry = "My card")
        MasterHandler.sendContent(self, 'templates/myCard_uploadProfilePhoto.html', {
            'photoUploadLink': blobstore.create_upload_url('/uploadphotopost'),
        })
        MasterHandler.sendBottomTemplate(self)

#-----------------------------------------------------------------------------

#TODO: Remove the previous photo of the user or add some photo management feature (e.g. different photos for different groups)
class UploadHandler(blobstore_handlers.BlobstoreUploadHandler):
    def post(self):
        upload_files = self.get_uploads('file')  # 'file' is file upload field in the form
        blob_info = upload_files[0]
        user = users.get_current_user()
        userProfile = UserProfile.all().filter("user =", user).get()
        userProfile.photograph = blob_info.key()
        userProfile.put()
        self.redirect('/profile')  # go back to the profile viewer

#-----------------------------------------------------------------------------

class ServeHandler(blobstore_handlers.BlobstoreDownloadHandler):
    def get(self, resource):
        resource = str(urllib.unquote(resource))
        logging.info("Getting a blob " + resource)
        blob_info = blobstore.BlobInfo.get(resource)
        self.send_blob(blob_info)

#-----------------------------------------------------------------------------

app = webapp2.WSGIApplication([
    ('/profile', ViewProfile),
    ('/editprofile', EditProfile),
    ('/submitprofile', EditProfile),
    ('/uploadphoto', UploadPhoto),
    ('/uploadphotopost', UploadHandler),
    ('/serveimageblob/([^/]+)?', ServeHandler),
], debug=True)
