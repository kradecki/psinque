# -*- coding: utf-8 -*-

import jinja2
import os
import logging
import urllib
import webapp2
import datetime

from google.appengine.api import users, datastore_errors
from google.appengine.ext import db
from google.appengine.ext import blobstore
from google.appengine.ext.webapp import blobstore_handlers
from google.appengine.api import images

from DataModels import UserProfile, UserSettings, Group
from DataModels import UserEmail, UserIM, UserWebpage, UserPhoneNumber, UserAddress, UserPhoto, UserNickname, UserCompany
from DataModels import Persona, PermitEmail, PermitIM, PermitWebpage, PermitPhoneNumber, PermitAddress
from DataModels import genders, imTypes, wwwTypes, phoneTypes, privacyTypes, monthNames, countries

from DataManipulation import generateVCard, createNewProfile, createNewGroup, createNewPersona

from MasterHandler import MasterHandler, AjaxError

#-----------------------------------------------------------------------------

class ProfileHandler(MasterHandler):

    #****************************
    # Private methods
    #

    def _updateAllVCards(self):

        for persona in Persona.all().ancestor(self.userProfile):
            generateVCard(persona)


    def _getItemByKey(self, itemClass):

        key = self.getRequiredParameter('key')
        
        try:
            item = itemClass.get(key)
        except datastore_errors.BadKeyError:
            raise AjaxError("Profile item not found.")
          
        return item
      
    
    def _checkNewItemByName(self, itemClass, itemValueName):

        itemValue = self.getRequiredParameter(itemValueName)

        # Check if this email has already been registered:
        try:
            existingItem = itemClass.all(keys_only = True). \
                                    filter(itemValueName + " =", itemValue). \
                                    get()

        except datastore_errors.BadKeyError:
            raise AjaxError(itemValueName + ": " + itemValue + " already registered in the system")
          
        return itemValue


    def _removeItem(self, itemClass):
      
        item = self._getItemByKey(itemClass)
        
        for individualPermit in item.individualPermits:
            individualPermit.delete()
        item.delete()

        self._updateAllVCards()
          

    #****************************
    # Views
    #

    def view(self):   # form for editing details

        userProfile = UserProfile.all().filter("user =", self.user).get()
        firstLogin = (not userProfile)

        if firstLogin:  # no user profile registered yet, so create a new one
            userProfile = createNewProfile(self.user)

        self.sendContent('templates/Profile.html',
                         activeEntry = "Profile",
                         templateVariables = {
            'firstlogin': firstLogin,
            'userProfile': userProfile,
            'months': monthNames,
            'primaryEmail': userProfile.emails.filter("primary =", True).get(),
            'additionalEmails': userProfile.emails.filter("primary =", False).order('-creationTime').fetch(limit = 1000),
            'phones': userProfile.phones.order('-creationTime').fetch(limit = 1000),
            'ims': userProfile.ims.order('-creationTime').fetch(limit = 1000),
            'wwws': userProfile.webpages.order('-creationTime').fetch(limit = 1000),
            'addresses': userProfile.addresses.order('-creationTime').fetch(limit = 1000),
            'nicknames': userProfile.nicknames.order('-creationTime').fetch(limit = 1000),
            'companies': userProfile.companies.order('-creationTime').fetch(limit = 1000),
            'genders': genders,
            'countries': countries,
            'imTypes': { x:imTypes for x in privacyTypes },
            'wwwTypes': { x:wwwTypes for x in privacyTypes },
            'phoneTypes': { x:phoneTypes for x in privacyTypes },
            'privacyTypes': privacyTypes,
        })


    #****************************
    # AJAX methods
    #

    def updategeneral(self):

        try:
            birthday   = int(self.getRequiredParameter('day'))
            birthyear  = int(self.getRequiredParameter('year'))
            birthmonth = int(self.getRequiredParameter('month'))
        except ValueError as e:
            raise AjaxError("Invalid integer number: " + str(e))

        self.userProfile.namePrefix = self.request.get('prefix')
        self.userProfile.nameSuffix = self.request.get('suffix')
        self.userProfile.givenNames = self.getRequiredParameter('givennames')
        self.userProfile.givenNamesRomanization = self.request.get('givenroman')
        self.userProfile.familyNames = self.getRequiredParameter('familynames')
        self.userProfile.familyNamesRomanization = self.request.get('familyroman')
        self.userProfile.companyName = self.request.get('company')
        self.userProfile.companyNameRomanization = self.request.get('companyroman')        
        self.userProfile.birthDate = datetime.date(birthyear, birthmonth, birthday)
        self.userProfile.gender = self.getRequiredParameter('gender')
        
        self.userProfile.put()

        self._updateAllVCards()

        self.sendJsonOK()


    def addemail(self):

        userEmail = UserEmail(parent = self.userProfile,
                              itemValue = self._checkNewItemByName(UserEmail, 'email'),
                              privacyType = self.getRequiredParameter('privacy'),
                              primary = self.getRequiredBoolParameter('primary'))
        userEmail.put()

        # Add permissions for this email in every outgoing group
        for persona in self.userProfile.personas:
            permitEmail = PermitEmail(parent = persona,
                                      userEmail = userEmail)
            permitEmail.put()

        self._updateAllVCards()

        self.sendJsonOK({'key': str(userEmail.key())})


    def updateemail(self):

        userEmail = self._getItemByKey(UserEmail)
        userEmail.itemValue = self.getRequiredParameter('email')
        userEmail.privacyType = self.getRequiredParameter('privacy')
        userEmail.put()

        self._updateAllVCards()

        self.sendJsonOK()


    def removeemail(self):

        userEmail = self._getItemByKey(UserEmail)

        if userEmail.primary:   # you cannot remove the primary email

            userEmail.itemValue = "primary@nonexistant.com"
            userEmail.privacyType = 'Home'
            userEmail.put()

        else:

            for permitEmail in userEmail.individualPermits:
                permitEmail.delete()
            userEmail.delete()

            self._updateAllVCards()

        self.sendJsonOK()


    def addim(self):

        userIM = UserIM(parent = self.userProfile,
                        itemValue = db.IM(imTypes[self.getRequiredParameter('type')],
                                          self.getRequiredParameter('im')),
                        privacyType = self.getRequiredParameter('privacy'))
        userIM.put()

        # Add permissions for this email in every outgoing group
        for persona in self.userProfile.personas:
            permitIM = PermitIM(parent = persona,
                                userIM = userIM)
            permitIM.put()

        self._updateAllVCards()

        self.sendJsonOK({'key': str(userIM.key())})


    def updateim(self):

        userIM = self._getItemByKey(UserIM)
        userIM.itemValue = db.IM(imTypes[self.getRequiredParameter('type')],
                                 self.getRequiredParameter('im'))
        userIM.privacyType = self.getRequiredParameter('privacy')
        userIM.put()

        self._updateAllVCards()

        self.sendJsonOK()


    def removeim(self):

        self._removeItem(UserIM)
        self.sendJsonOK()


    def addwww(self):

        userWebpage = UserWebpage(parent = self.userProfile,
                                  itemValue = self.getRequiredParameter('www'),
                                  privacyType = self.getRequiredParameter('privacy'),
                                  itemType = self.getRequiredParameter('type'))
        userWebpage.put()

        # Add permissions for this email in every outgoing group
        for persona in self.userProfile.personas:
            permitWebpage = PermitWebpage(parent = persona,
                                          userWebpage = userWebpage)
            permitWebpage.put()

        self._updateAllVCards()

        self.sendJsonOK({'key': str(userWebpage.key())})


    def updatewww(self):

        userWebpage = self._getItemByKey(UserWebpage)
        userWebpage.itemValue = self.getRequiredParameter('www')
        userWebpage.itemType = self.getRequiredParameter('type')
        userWebpage.privacyType = self.getRequiredParameter('privacy')
        userWebpage.put()

        self._updateAllVCards()

        self.sendJsonOK()


    def removewww(self):

        self._removeItem(UserWebpage)
        self.sendJsonOK()


    def addphone(self):

        userPhone = UserPhoneNumber(parent = self.userProfile,
                                    itemValue = self._checkNewItemByName(UserPhoneNumber, 'phone'),
                                    privacyType = self.getRequiredParameter('privacy'),
                                    itemType = self.getRequiredParameter('type'))
        userPhone.put()

        # Add permissions for this email in every outgoing group
        for persona in self.userProfile.personas:
            permitPhone = PermitPhoneNumber(parent = persona,
                                            userPhoneNumber = userPhone)
            permitPhone.put()

        self._updateAllVCards()

        self.sendJsonOK({'key': str(userPhone.key())})


    def updatephone(self):

        userPhone = self._getItemByKey(UserPhoneNumber)
        userPhone.itemValue = self.getRequiredParameter('phone')
        userPhone.itemType = self.getRequiredParameter('type')
        userPhone.privacyType = self.getRequiredParameter('privacy')
        userPhone.put()

        self._updateAllVCards()

        self.sendJsonOK()


    def removephone(self):
 
        self._removeItem(UserPhoneNumber)
        self.sendJsonOK()
        
        
    def removephoto(self):

        key = self.getRequiredParameter('key')

        try:
            photo = UserPhoto.get(key)
            
            for persona in Persona.all().filter("picture =", photo):
                persona.picture = None
                persona.put()
              
            photo.image.delete()
            photo.delete()
            
            self.sendJsonOK()

        except datastore_errors.BadKeyError:
            raise AjaxError("Photo not found.")


    def addaddress(self):

        longitude = self.request.get("lon")
        latitude  = self.request.get("lat")
        if longitude != "" and latitude != "":
            location = db.GeoPt(latitude, longitude)
        else:
            location = None
            
        countryCode = self.getRequiredParameter('country')
        if countryCode == "Country":
            countryCode = ""

        userAddress = UserAddress(parent = self.userProfile,
                                  address = self.getRequiredParameter('address'),
                                  city = self.getRequiredParameter('city'),
                                  countryCode = countryCode,
                                  postalCode = self.request.get('postal'),
                                  privacyType = self.getRequiredParameter('privacy'),
                                  location = location)
        userAddress.put()

        # Add permissions for this email in every outgoing group
        for persona in self.userProfile.personas:
            permitAddress = PermitAddress(parent = persona,
                                          userAddress = userAddress)
            permitAddress.put()

        self._updateAllVCards()

        self.sendJsonOK({'key': str(userAddress.key())})


    def updateaddress(self):

        longitude = self.request.get("lon")
        latitude  = self.request.get("lat")
        if longitude != "" and latitude != "":
            location = db.GeoPt(latitude, longitude)
        else:
            location = None

        countryCode = self.getRequiredParameter('country')
        if countryCode == "Country":
            countryCode = ""

        userAddress = self._getItemByKey(UserAddress)
        userAddress.address = self.getRequiredParameter('address')
        userAddress.city = self.getRequiredParameter('city')
        userAddress.postalCode = self.request.get('postal')
        userAddress.countryCode = countryCode
        userAddress.privacyType = self.getRequiredParameter('privacy')
        userAddress.location = location
        userAddress.put()

        self._updateAllVCards()

        self.sendJsonOK()


    def removeaddress(self):
 
        self._removeItem(UserAddress)
        self.sendJsonOK()
        
      
    def getphotouploadurl(self):
      
        uploadURL = blobstore.create_upload_url('/uploadphoto')
        self.response.headers['Content-Type'] = 'application/json'
        self.response.out.write('"' + uploadURL + '"')
        
        
    def getfullphoto(self):

        key = self.getRequiredParameter('key')
        width = self.getRequiredParameter('width')
        height = self.getRequiredParameter('height')
        
        self.sendContent('templates/profile/FullPhoto.html',
                         templateVariables = {
            'key': key,
            'width': width,
            'height': height,
        })
                         
                         
    def addnickname(self):

        userNickname = UserNickname(parent = self.userProfile,
                                    itemValue = self.getRequiredParameter('nickname'))
        userNickname.put()

        self._updateAllVCards()

        self.sendJsonOK({'key': str(userNickname.key())})


    def updatenickname(self):

        userNickname = self._getItemByKey(UserNickname)
        userNickname.itemValue = self.getRequiredParameter('nickname')
        userNickname.put()

        self._updateAllVCards()

        self.sendJsonOK()


    def removenickname(self):
 
        item = self._getItemByKey(UserNickname)
        item.delete()
        
        self.sendJsonOK()
        
        
    def addcompany(self):

        userCompany = UserCompany(parent = self.userProfile,
                                  companyName = self.getRequiredParameter('company'),
                                  positionName = self.request.get('position'))
        userCompany.put()

        self._updateAllVCards()

        self.sendJsonOK({'key': str(userCompany.key())})


    def updatecompany(self):

        userCompany = self._getItemByKey(UserCompany)
        userCompany.companyName = self.getRequiredParameter('company')
        userCompany.positionName = self.request.get('position')
        userCompany.put()

        self._updateAllVCards()

        self.sendJsonOK()


    def removecompany(self):
 
        item = self._getItemByKey(UserCompany)
        item.delete()
        
        self.sendJsonOK()
        

        
#-----------------------------------------------------------------------------

jinja_environment = jinja2.Environment(
    loader = jinja2.FileSystemLoader(os.path.dirname(__file__))
)

class UploadHandler(blobstore_handlers.BlobstoreUploadHandler):

    def post(self):
      
        upload_files = self.get_uploads('files[]')  # 'file' is file upload field in the form
        blob_info = upload_files[0]
        
        img = images.Image(blob_key=str(blob_info.key()))
        
        # we must execute a transform to access the width/height
        img.im_feeling_lucky() # do a transform, otherwise GAE complains.

        # set quality to 1 so the result will fit in 1MB if the image is huge
        img.execute_transforms(output_encoding=images.JPEG,quality=1)

        user = users.get_current_user()
        userProfile = UserProfile.all().filter("user =", user).get()
        userPhoto = UserPhoto(parent = userProfile,
                              image = blob_info.key(),
                              width = img.width,
                              height = img.height,
                              servingUrl = images.get_serving_url(blob_info.key()))
        userPhoto.put()
        
        #self.response.headers['Content-Type'] = 'application/json'
        #self.response.out.write('"' + userPhoto.servingUrl + '=s162"')
                         
        template = jinja_environment.get_template('templates/profile/Thumbnail.html')
        self.response.out.write(template.render({
            'photo': userPhoto,
        }))

#-----------------------------------------------------------------------------

class ServeHandler(blobstore_handlers.BlobstoreDownloadHandler):
  
    def get(self, resource):
      
        resource = str(urllib.unquote(resource))
        blob_info = blobstore.BlobInfo.get(resource)
        self.send_blob(blob_info)

#-----------------------------------------------------------------------------

app = webapp2.WSGIApplication([
    (r'/profile/(\w+)', ProfileHandler),
    ('/uploadphoto', UploadHandler),
    ('/serveimageblob/([^/]+)?', ServeHandler),
], debug=True)
