# -*- coding: utf-8 -*-

import os
import logging
import urllib
import webapp2

from google.appengine.api import users
from google.appengine.ext import blobstore
from google.appengine.ext.webapp import blobstore_handlers

from DataModels import UserProfile, UserEmail, UserSettings, Group
from DataModels import Permit, PermitEmail
from DataModels import emailTypes, addressTypes

from MasterHandler import MasterHandler, AjaxError

#-----------------------------------------------------------------------------

class ProfileHandler(MasterHandler):

    #****************************
    # Private methods
    # 

    def _updateAllVCards(self):
        
        for permit in Permit.all().ancestor(self.userProfile):
            permit.generateVCard()
            permit.put()


    def _createNewProfile(self):
        
        logging.info("Creating new profile")
        
        # Create an empty profile
        userProfile = UserProfile(user = self.user)
        userProfile.put()  # save the new (and empty) profile in the Datastore in order to obtain its key
        
        # User settings
        userSettings = UserSettings(parent = userProfile)
        userSettings.put()
        userProfile.userSettings = userSettings
        
        # Primary email address (needed for notifications, etc.)
        userEmail = UserEmail(parent = userProfile,
                              email = "primary@nonexistant.com",
                              emailType = 'private',
                              primary = True)
        userEmail.put()
                
        # Default group
        defaultGroup = Group(parent = userProfile,
                             name = 'Default')
        defaultGroup.put()
        userProfile.defaultGroup = defaultGroup
        
        # Default private permit
        defaultPermit = Permit(parent = userProfile,
                               name = "Default")
        defaultPermit.put()

        userProfile.defaultPermit = defaultPermit

        defaultPermitEmail = PermitEmail(parent = defaultPermit,
                                         userEmail = userEmail)
        defaultPermitEmail.put()
        
        defaultPermit.generateVCard()
        defaultPermit.put()

        # Public permit
        publicPermit = Permit(parent = userProfile,
                              name = "Public",
                              public = True)
        publicPermit.put()

        userProfile.publicPermit = publicPermit

        publicPermitEmail = PermitEmail(parent = publicPermit,
                                        userEmail = userEmail)
        publicPermitEmail.put()
        publicPermit.put()

        publicPermit.generateVCard()
        
        # Save the updated user profile
        userProfile.put()
        
        logging.info("Profile created")
        return userProfile
        
    #****************************
    # Views
    # 
    
    def view(self):   # form for editing details

        userProfile = UserProfile.all().filter("user =", self.user).get()
        firstLogin = (not userProfile)

        if firstLogin:  # no user profile registered yet, so create a new one
          userProfile = self._createNewProfile()

        #userAddresses = userProfile.addresses.fetch(100)
        #addresses = map(lambda x: {'nr': str(x+1), 'value': userAddresses[x]}, range(0, len(userAddresses)))
        #if len(addresses) == 0:
            #addresses = [{'nr': 1, 'value': None}]

        primaryEmail = userProfile.emails.filter("primary =", True).get()
        additionalEmails = userProfile.emails.filter("primary =", False).fetch(limit = 1000)
            
        self.sendContent('templates/myCard_view.html',
                         activeEntry = "My card",
                         templateVariables = {
            'firstlogin': firstLogin,
            'userProfile': userProfile,
            'primaryEmail': primaryEmail,
            'additionalEmails': additionalEmails,
            #'anyAdditionalEmails': anyAdditionalEmails,
            'emailTypes': emailTypes,
            #'addresses': addresses,
            #'addressTypes': addressTypes,
        })
            
    #****************************
    # AJAX methods
    # 
    
    def updategeneral(self):
        
        firstname = self.getRequiredParameter('firstname')
        lastname = self.getRequiredParameter('lastname')

        self.userProfile.givenNames = [ firstname ]
        self.userProfile.familyNames = [ lastname ]
        self.userProfile.put()
        
        self._updateAllVCards()
        
        self.sendJsonOK()
    
    
    def addemail(self):
        
        email = self.getRequiredParameter('email')
        emailType = self.getRequiredParameter('type')
        
        # Check if this email has already been registered:
        existingEmail = UserEmail.all(keys_only = True). \
                                  filter("email =", email). \
                                  get()
        if not existingEmail is None:
            raise AjaxError("Email is already registered in the system")
        
        userEmail = UserEmail(parent = self.userProfile,
                              email = email,
                              emailType = emailType)
        userEmail.put()
        
        # Add permissions for this email in every outgoing group
        for permit in self.userProfile.permits:
            permitEmail = PermitEmail(parent = permit,
                                      userEmail = userEmail)
            permitEmail.put()
            
        self._updateAllVCards()

        self.sendJsonOK({'key': str(userEmail.key())})


    def updateemail(self):
        
        emailKey = self.getRequiredParameter('key')
        email = self.getRequiredParameter('email')
        emailType = self.getRequiredParameter('type')
        
        userEmail = UserEmail.get(emailKey)
        userEmail.email = email
        userEmail.emailType = emailType
        userEmail.put()
        
        self._updateAllVCards()

        self.sendJsonOK()


    def removeemail(self):
        
        emailKey = self.getRequiredParameter('key')
            
        userEmail = UserEmail.get(emailKey)
        if userEmail is None:
            raise AjaxError("User email not found.")
        
        for permitEmail in userEmail.permitEmails:
            permitEmail.delete()
        userEmail.delete()

        self._updateAllVCards()

        self.sendJsonOK()
            
            
    def addim(self):
        self.sendJsonError("Unimplemented")
            
            
    def updateim(self):
        self.sendJsonError("Unimplemented")
            
            
    def removeim(self):
        self.sendJsonError("Unimplemented")


    def addwww(self):
        self.sendJsonError("Unimplemented")
            
            
    def updatewww(self):
        self.sendJsonError("Unimplemented")
            
            
    def removewww(self):
        self.sendJsonError("Unimplemented")


    def addphone(self):
        self.sendJsonError("Unimplemented")
            
            
    def updatephone(self):
        self.sendJsonError("Unimplemented")
            
            
    def removephone(self):
        self.sendJsonError("Unimplemented")
            
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
        self.redirect('/mycard/view')  # go back to the profile viewer

#-----------------------------------------------------------------------------

class ServeHandler(blobstore_handlers.BlobstoreDownloadHandler):
    def get(self, resource):
        resource = str(urllib.unquote(resource))
        logging.info("Getting a blob " + resource)
        blob_info = blobstore.BlobInfo.get(resource)
        self.send_blob(blob_info)

#-----------------------------------------------------------------------------

app = webapp2.WSGIApplication([
    (r'/mycard/(\w+)', ProfileHandler),
    ('/uploadphoto', UploadPhoto),
    ('/uploadphotopost', UploadHandler),
    ('/serveimageblob/([^/]+)?', ServeHandler),
], debug=True)
