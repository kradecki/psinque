
import os
import logging
import urllib
import webapp2

from google.appengine.ext import db
from google.appengine.api import users
from google.appengine.ext import blobstore
from google.appengine.ext.webapp import blobstore_handlers

from MasterHandler import MasterHandler, AjaxError
from CardDAV import CardDAVPassword
from vobject import vcard

#-----------------------------------------------------------------------------
# Data models

genders    = ["male", "female"]
phoneTypes = ["home landline", "private cellphone", "work cellphone", "work landline", "home fax", "work fax", "other"]
addressTypes = {'home': 'Home', 'work': 'Work'}
emailTypes   = {'private': 'Private', 'work': 'Work'}

class UserProfile(db.Model):

    user = db.UserProperty()

    givenNames = db.ListProperty(required = True)
    lastName = db.StringProperty(required = True)
    pseudonyms = db.ListProperty(required = False)
    companyName = db.StringProperty(required = False)

    gender = db.StringProperty(choices = genders,
                                required = False)

    birthDay = db.DateProperty()  

    # nationality? namesday?

    @property
    def vcardName(self):
        vcard.Name(family = UserProfile.lastName,
                   given = UserProfile.givenNames[0])

    @property
    def fullName(self):
        if not middleName is None:
            return UserProfile.firstName + " " +
                   UserProfile.middleName + " " +
                   UserProfile.lastName
        else:
            return UserProfile.firstName + " " +
                   UserProfile.lastName
     
    @property
    def emails(self):
        return UserEmail.all().ancestor(UserProfile)

#class UserPhoto(db.Model):
  #user = db.ReferenceProperty(UserProfile, collection_name = "photos")
  #photograph = blobstore.BlobReferenceProperty()

class UserAddress(db.Model):
  #user = db.ReferenceProperty(UserProfile, collection_name = "addresses")
  address = db.PostalAddressProperty()
  city = db.StringProperty()
  postalCode = db.StringProperty()
  addressType = db.StringProperty(choices = addressTypes.keys())
  location = db.GeoPtProperty()

class UserEmail(db.Model):
  #user = db.ReferenceProperty(UserProfile, collection_name = "emails")
  email = db.EmailProperty()
  emailType = db.StringProperty(choices = emailTypes.keys())
  primary = db.BooleanProperty()

class UserIM(db.Model):
  #user = db.ReferenceProperty(UserProfile)
  im = db.IMProperty()

class UserPhoneNumber(db.Model):
  #user = db.ReferenceProperty(UserProfile, collection_name = "phoneNumbers")
  phone = db.PhoneNumberProperty(required = True)
  phoneType = db.StringProperty(choices = phoneTypes)

class UserWebpage(db.Model):
  #user = db.ReferenceProperty(UserProfile)
  address = db.StringProperty()
  webpageType = db.StringProperty(choices = ["private homepage", "business homepage", "facebook", "myspace", "other"])

#-----------------------------------------------------------------------------
# Request handler

class ProfileHandler(MasterHandler):

    def edit(self):   # form for editing details

        userProfile = UserProfile.all().filter("user =", self.user).get()
        firstLogin = (not userProfile)

        if firstLogin:  # no user profile registered yet, so create a new one
        
            userProfile = UserProfile(user = self.user)
            userProfile.put()  # save the new (and empty) profile in the Datastore
            
            userSettings = UserSettings(parent = userProfile, user = self.user)
            userSettings.put()
            
            #cardDAVPassword = CardDAVPassword(parent = userSettings,
                                              #user = self.user,
                                              #generatedUsername = 'dupa',
                                              #generatedPassword = 'dupa')
            #cardDAVPassword.put()

            # Default groups and permits
            defaultGroup = Group(parent = userProfile,
                                 name = 'Default')
            defaultGroup.put()
            
            defaultPermit = Permit(parent = userProfile,
                                   name = "Default")
            defaultPermit.generateVCard()
            defaultPermit.put()

            publicPermit = Permit(parent = userProfile,
                                  name = "Public",
                                  public = True)
            publicPermit.generateVCard()
            publicPermit.put()

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
