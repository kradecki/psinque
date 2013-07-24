# -*- coding: utf-8 -*-

import os
import logging
import urllib
import webapp2
import datetime

from google.appengine.api import users
from google.appengine.ext import blobstore
from google.appengine.ext.webapp import blobstore_handlers

from DataModels import UserProfile, UserSettings, Group, UserEmail
from DataModels import Permit, PermitEmail
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


    #****************************
    # Views
    #

    def view(self):   # form for editing details

        userProfile = UserProfile.all().filter("user =", self.user).get()
        firstLogin = (not userProfile)

        if firstLogin:  # no user profile registered yet, so create a new one
          userProfile = self._createNewProfile()

        userAddresses = userProfile.addresses.fetch(limit = 1000)
        ims  = userProfile.ims.fetch(limit = 1000)
        webpages = userProfile.webpages.fetch(limit = 1000)

        primaryEmail = userProfile.emails.filter("primary =", True).get()
        additionalEmails = userProfile.emails.filter("primary =", False).fetch(limit = 1000)
        phones = userProfile.phones.filter("primary =", False).fetch(limit = 1000)

        self.sendContent('templates/MyCard.html',
                         activeEntry = "My card",
                         templateVariables = {
            'firstlogin': firstLogin,
            'userProfile': userProfile,
            'months': monthNames,
            'primaryEmail': primaryEmail,
            'additionalEmails': additionalEmails,
            'phones': phones,
            'ims': ims,
            'wwws': webpages,
            'addresses': userAddresses,
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
        self.userProfile.givenNamesRomanization = self.getRequiredParameter('givenroman')
        self.userProfile.familyNames = self.getRequiredParameter('familynames')
        self.userProfile.familyNamesRomanization = self.getRequiredParameter('familyroman')
        self.userProfile.companyName = self.getRequiredParameter('company')
        self.userProfile.companyNameRomanization = self.getRequiredParameter('companyroman')        
        self.userProfile.birthDate = datetime.date(birthyear, birthmonth, birthday)
        self.userProfile.gender = self.getRequiredParameter('gender')
        
        self.userProfile.put()

        self._updateAllVCards()

        self.sendJsonOK()


    def addemail(self):

        email = self.getRequiredParameter('email')
        privacyType = self.getRequiredParameter('privacy')
        isPrimary = self.getRequiredBoolParameter('primary')

        # Check if this email has already been registered:
        existingEmail = UserEmail.all(keys_only = True). \
                                  filter("email =", email). \
                                  get()
        if not existingEmail is None:
            raise AjaxError("Email is already registered in the system")

        userEmail = UserEmail(parent = self.userProfile,
                              itemValue = email,
                              privacyType = privacyType,
                              primary = isPrimary)
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
        privacyType = self.getRequiredParameter('privacy')

        userEmail = UserEmail.get(emailKey)
        userEmail.itemValue = email
        userEmail.privacyType = privacyType
        userEmail.put()

        self._updateAllVCards()

        self.sendJsonOK()


    def removeemail(self):

        emailKey = self.getRequiredParameter('key')

        userEmail = UserEmail.get(emailKey)
        if userEmail is None:
            raise AjaxError("User email not found.")

        if userEmail.primary:

            userEmail.itemValue = "primary@nonexistant.com"
            userEmail.privacyType = 'Home'
            userEmail.put()

        else:

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
