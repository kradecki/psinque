
import os
import logging
import urllib
import webapp2

from google.appengine.ext import db
from google.appengine.api import users
from google.appengine.ext import blobstore
from google.appengine.ext.webapp import blobstore_handlers

from MasterHandler import MasterHandler, AjaxError
from users.UserDataModels import UserProfile, UserSettings, UserAddress, UserEmail
from users.UserDataModels import UserGroup, CardDAVPassword
from users.UserDataModels import PermissionEmail

# Available data type choices:
from users.UserDataModels import availableLanguages, addressTypes, emailTypes

#-----------------------------------------------------------------------------

class ProfileHandler(MasterHandler):

    def get(self, actionName):
        
        if MasterHandler.safeGuard(self):
            
            actionFunction = getattr(self, actionName)
            
            try:
                actionFunction()
            except AjaxError as e:
                self.sendJsonError(e.value)

    def view(self):

        if self.getUserProfile():
            #if userProfile.photograph != None:
            #template_values['photograph'] = '/serveimageblob/%s' % serProfile.photograph.key()
            
            self.sendTopTemplate(activeEntry = "My card")
            self.sendContent('templates/myCard_view.html', {
                'userProfile': self.userProfile,
            })
            self.sendBottomTemplate()

    def edit(self):   # form for editing details

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
            
            publicGroup = UserGroup(parent = userProfile,
                                    creator = userProfile,
                                    name = 'Public')
            publicGroup.put()

            userEmail = UserEmail(parent = userProfile,
                                  user = userProfile,
                                  email = "primary@nonexistant.com",
                                  emailType = 'private',
                                  primary = True)
            userEmail.put()
            
            permissionEmail = PermissionEmail(parent = publicGroup,
                                              userGroup = publicGroup,
                                              emailAddress = userEmail)
            permissionEmail.put()
        
        userAddresses = userProfile.addresses.ancestor(userProfile).fetch(100)
        addresses = map(lambda x: {'nr': str(x+1), 'value': userAddresses[x]}, range(0, len(userAddresses)))
        if len(addresses) == 0:
            addresses = [{'nr': 1, 'value': None}]
            
        userEmails = userProfile.emails.ancestor(userProfile).order("-primary")
        
        template_values = {
            'firstlogin': firstLogin,
            'userProfile': userProfile,
            'userEmails': userEmails,
            'emailTypes': emailTypes,
            'addresses': addresses,
            'addressTypes': addressTypes,
            }
            
        self.sendTopTemplate(activeEntry = "My card")
        self.sendContent('templates/myCard_edit.html', template_values)
        self.sendBottomTemplate()
    
    def updategeneral(self):
        
        if self.getUserProfile():
            
            firstname = self.checkGetParameter('firstname')
            lastname = self.checkGetParameter('lastname')

            self.userProfile.firstName = firstname
            self.userProfile.middleName = self.request.get("middlename")
            self.userProfile.lastName = lastname
            self.userProfile.put()
            
            self.sendJsonOK()
    
    def addemail(self):
        
        if self.getUserProfile():
            
            email = self.checkGetParameter('email')
            emailType = self.checkGetParameter('emailType')
            
            userEmail = UserEmail(parent = self.userProfile,
                                  user = self.userProfile,
                                  email = email,
                                  emailType = emailType)
            userEmail.put()
            
            # Add permissions for this email in every outgoing group
            for userGroup in self.userProfile.groups:
                permissionEmail = PermissionEmail(userGroup = userGroup,
                                                  emailAddress = userEmail)
                permissionEmail.put()
                
            self.sendJsonOK({'key': str(userEmail.key())})

    def updateemail(self):
        
        if self.getUserProfile():
            
            emailKey = self.checkGetParameter('emailKey')
            email = self.checkGetParameter('email')
            emailType = self.checkGetParameter('emailType')
            
            userEmail = UserEmail.get(emailKey)
            userEmail.email = email
            userEmail.emailType = emailType
            userEmail.put()
            
            self.sendJsonOK()

    def removeemail(self):
        
            emailKey = self.checkGetParameter('emailKey')
               
            userEmail = UserEmail.get(self.emailKey)
            if userEmail is None:
                raise AjaxError("User email not found.")
            
            for permissionEmail in userEmail.permissionEmails:
                permissionEmail.delete()
            userEmail.delete()

            self.sendJsonOK()
            
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
