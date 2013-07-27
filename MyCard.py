# -*- coding: utf-8 -*-

import os
import logging
import urllib
import webapp2
import datetime

from google.appengine.api import users
from google.appengine.ext import db
from google.appengine.ext import blobstore
from google.appengine.ext.webapp import blobstore_handlers

from DataModels import UserProfile, UserSettings, Group
from DataModels import UserEmail, UserIM, UserWebpage, UserPhoneNumber, UserAddress
from DataModels import Permit, PermitEmail, PermitIM, PermitWebpage, PermitPhoneNumber, PermitAddress
from DataModels import genders, imTypes, wwwTypes, phoneTypes, privacyTypes, monthNames

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


    def _createNewPermit(self, userProfile, permitName, userEmail):

        permit = Permit(parent = userProfile,
                        name = permitName)
        permit.put()

        permitEmail = PermitEmail(parent = permit,
                                  userEmail = userEmail)
        permitEmail.put()

        permit.generateVCard()
        permit.put()

        logging.info("New permit created, key = " + str(permit.key()))

        return permit


    def _createNewGroup(self, userProfile, groupName):

        group = Group(parent = userProfile,
                      name = groupName)
        group.put()

        #logging.info("New group created, key = " + str(group.key()))

        return group


    def _createNewProfile(self):

        # Create an empty profile
        userProfile = UserProfile(user = self.user)
        userProfile.put()  # save the new (and empty) profile in the Datastore in order to obtain its key

        # User settings
        userSettings = UserSettings(parent = userProfile)
        userSettings.put()
        userProfile.userSettings = userSettings

        # Primary email address (needed for notifications, etc.)
        userEmail = UserEmail(parent = userProfile,
                              itemValue = "primary@nonexistant.com",
                              privacyType = 'Home',
                              primary = True)
        userEmail.put()

        userProfile.defaultGroup = self._createNewGroup(userProfile,
                                                        'Default')

        userProfile.defaultPermit = self._createNewPermit(userProfile,
                                                          'Default',
                                                          userEmail)

        userProfile.publicPermit = self._createNewPermit(userProfile,
                                                          'Public',
                                                          userEmail)

        # Save the updated user profile
        userProfile.put()

        logging.info("New profile created")
        return userProfile


    def _getItemByKey(self, itemClass):

        key = self.getRequiredParameter('key')

        item = itemClass.get(key)
        if item is None:
            raise AjaxError("Profile item not found.")
          
        return item
      
    
    def _checkNewItemByName(self, itemClass, itemValueName):

        itemValue = self.getRequiredParameter(itemValueName)

        # Check if this email has already been registered:
        existingItem = itemClass.all(keys_only = True). \
                                 filter(itemValueName + " =", itemValue). \
                                 get()
        if not existingItem is None:
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
          userProfile = self._createNewProfile()

        self.sendContent('templates/MyCard.html',
                         activeEntry = "My card",
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
            'genders': genders,
            'privacyTypes': privacyTypes,
            'imTypes': imTypes,
            'wwwTypes': wwwTypes,
            'phoneTypes': phoneTypes,
        })


    #****************************
    # AJAX methods
    #

    def updategeneral(self):

        try:
            birthday   = int(self.getRequiredParameter('day'))
            birthyear  = int(self.getRequiredParameter('year'))
        except ValueError as e:
            raise AjaxError("Invalid integer number: " + str(e))

        birthmonth = self.getRequiredParameter('month')
        
        try:
            birthmonth = monthNames.index(birthmonth) + 1
        except ValueError:
            raise AjaxError("Invalid month name: " + birthmonth)

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
        for permit in self.userProfile.permits:
            permitEmail = PermitEmail(parent = permit,
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
                        itemValue = db.IM(self.getRequiredParameter('type'),
                                          self.getRequiredParameter('im')),
                        privacyType = self.getRequiredParameter('privacy'))
        userIM.put()

        # Add permissions for this email in every outgoing group
        for permit in self.userProfile.permits:
            permitIM = PermitIM(parent = permit,
                                userIM = userIM)
            permitIM.put()

        self._updateAllVCards()

        self.sendJsonOK({'key': str(userIM.key())})


    def updateim(self):

        userIM = self._getItemByKey(UserIM)
        userIM.itemValue = db.IM(self.getRequiredParameter('type'),
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
        for permit in self.userProfile.permits:
            permitWebpage = PermitWebpage(parent = permit,
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
        for permit in self.userProfile.permits:
            permitPhone = PermitPhoneNumber(parent = permit,
                                            userPhone = userPhone)
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


    def addaddress(self):

        userAddress = UserAddress(parent = self.userProfile,
                                  address = self.getRequiredParameter('address'),
                                  city = self.getRequiredParameter('city'),
                                  countryCode = self.getRequiredParameter('country'),
                                  postalCode = self.request.get('postal'),
                                  privacyType = self.getRequiredParameter('privacy'),
                                  location = db.GeoPt(self.getRequiredParameter('lat'),
                                                      self.getRequiredParameter('lon')))
        userAddress.put()

        # Add permissions for this email in every outgoing group
        for permit in self.userProfile.permits:
            permitAddress = PermitAddress(parent = permit,
                                          userAddress = userAddress)
            permitAddress.put()

        self._updateAllVCards()

        self.sendJsonOK({'key': str(userAddress.key())})


    def updateaddress(self):

        userAddress = self._getItemByKey(UserAddress)
        userAddress.itemValue = self.getRequiredParameter('address')
        userAddress.city = self.getRequiredParameter('city')
        userAddress.postalCode = self.request.get('postal')
        userAddress.countryCode = self.getRequiredParameter('country')
        userAddress.itemType = self.getRequiredParameter('type')
        userAddress.privacyType = self.getRequiredParameter('privacy')
        userAddress.location = db.GeoPt(self.getRequiredParameter('lat'),
                                        self.getRequiredParameter('lon'))
        userAddress.put()

        self._updateAllVCards()

        self.sendJsonOK()


    def removeaddress(self):
 
        self._removeItem(UserAddress)
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
