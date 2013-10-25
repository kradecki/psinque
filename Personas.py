# -*- coding: utf-8 -*-

import logging
import webapp2

import pyqrcode
import StringIO

from google.appengine.api import users, datastore_errors
from google.appengine.ext.db import Key

from MasterHandler import MasterHandler, AjaxError
from DataModels import Persona, Contact
from DataModels import IndividualPermit, PermitEmail, PermitIM, PermitPhoneNumber, PermitWebpage, PermitAddress, UserPhoto

from DataManipulation import generateVCard, reallyGenerateVCard

#-----------------------------------------------------------------------------

class PersonasHandler(MasterHandler):

    #****************************
    # Private methods
    # 
    
    def _getPersonaByName(self, personaName):
      
      return Persona.all(). \
                      ancestor(self.userProfile). \
                      filter("name =", personaName). \
                      get()


    def _getPersonaUpdateVCard(self):
      
        personaKey = self.getRequiredParameter('key')
        persona = Persona.get(personaKey)
        if persona.vcardNeedsUpdating:
            reallyGenerateVCard(persona)
            
        return persona
      
      
    def _getNicknames(self):

        nicknames = self.userProfile.nicknames.order('-creationTime').fetch(limit = 1000)
        nicknames = { x.key(): x.itemValue for x in nicknames }
        nicknames["None"] = "None"
        return nicknames


    def _getCompanies(self):

        companies = self.userProfile.companies.order('-creationTime').fetch(limit = 1000)
        companies = { x.key(): x.companyName for x in companies }
        companies["None"] = "None"
        return companies
      
      
    def _getPhotos(self):
      
        photos = self.userProfile.photos.order('-creationTime').fetch(limit = 1000)
        return photos


    #****************************
    # Views
    # 
    
    def view(self):
        
        if self.getUserProfile():
          
            self.sendContent('templates/Personas.html',
                            activeEntry = "Personas",
                            templateVariables = {
                'userProfile': self.userProfile,
                'companies': self._getCompanies(),
                'nicknames': self._getNicknames(),
                'photos': self._getPhotos(),
                'personas': Persona.all(). \
                                  ancestor(self.userProfile). \
                                  order("name"),
            })


    #****************************
    # AJAX methods
    # 
    
    def removepersona(self):
        
        try:
            persona = Persona.get(self.getRequiredParameter('key'))
            
            # Check for errors
            if persona.name == "Public":  # cannot remove the public persona
                raise AjaxError("Cannot remove the public persona")
            if persona.name == "Default":  # cannot remove the default persona
                raise AjaxError("Cannot remove the default private persona")

            # Get all contacts that use this persona and assign them the default persona
            contacts = Contact.all(). \
                              ancestor(self.userProfile). \
                              filter("persona =", persona)
            defaultPersona = self._getPersonaByName("Default")
            for contact in contacts:
                contact.persona = defaultPersona

            # Remove all children individual permits
            individualPermits = IndividualPermit.all().ancestor(persona)
            for individualPermit in individualPermits:
                individualPermit.delete()
            persona.delete()  # and the persona itself

            self.sendJsonOK()

        except datastore_errors.BadKeyError:
            raise AjaxError("Persona not found")
            
            
    def addpersona(self):
        
        personaName = self.getRequiredParameter('name')
        personaIndex = self.getRequiredParameter('index')
        
        # Error checking
        if personaName == "Public":
            raise AjaxError("Cannot create another public persona")
        if personaName == "Default":
            raise AjaxError("Cannot create another default private persona")

        try:
            # Check if the persona already exists
            persona = self._getPersonaByName(personaName)

            # Create a new Persona
            newPersona = Persona(parent = self.userProfile,
                              name = personaName)
            newPersona.put()
            
            for email in self.userProfile.emails:
                permitEmail = PermitEmail(parent = newPersona,
                                          userEmail = email)
                permitEmail.put()
                
            for im in self.userProfile.ims:
                permitIM = PermitIM(parent = newPersona,
                                    userIM = im)
                permitIM.put()
                
            for www in self.userProfile.webpages:
                permitWebpage = PermitWebpage(parent = newPersona,
                                              userWebpage = www)
                permitWebpage.put()
                
            for phone in self.userProfile.phones:
                permitPhoneNumber = PermitPhoneNumber(parent = newPersona,
                                                      userPhoneNumber = phone)
                permitPhoneNumber.put()
                
            for address in self.userProfile.addresses:
                permitAddress = PermitAddress(parent = newPersona,
                                              userAddress = address)
                permitAddress.put()
            
            # Generate the Persona's vCard and eTag:
            generateVCard(newPersona)

            self.sendContent('templates/Personas_Persona.html',
                            activeEntry = "Personas",
                            templateVariables = {
                    'persona': newPersona,
                    'companies': self._getCompanies(),
                    'nicknames': self._getNicknames(),
                    'photos': self._getPhotos(),
                    'userProfile': self.userProfile,
                    'personaIndex': personaIndex,
                })

        except datastore_errors.BadKeyError:
            raise AjaxError("Persona with that name already exists")
    
    
    def setgeneral(self):

        try:
            persona = Persona.get(self.getRequiredParameter('key'))
              
            newName = self.request.get("name")
            if newName != "":
                persona.name = newName

            persona.canViewPrefix = self.getRequiredBoolParameter('prefix')
            persona.canViewGivenNames = self.getRequiredBoolParameter('givennames')
            persona.canViewRomanGivenNames = self.getRequiredBoolParameter('givennamesroman')
            persona.canViewFamilyNames = self.getRequiredBoolParameter('familynames')
            persona.canViewRomanFamilyNames = self.getRequiredBoolParameter('familynamesroman')
            persona.canViewSuffix = self.getRequiredBoolParameter('suffix')
            persona.canViewBirthday = self.getRequiredBoolParameter('birthday')
            persona.canViewGender = self.getRequiredBoolParameter('gender')
            
            company = self.request.get("company")
            if company != "None":
                persona.company = Key(company)
            else:
                persona.company = None
            
            nickname = self.request.get("nickname")
            if nickname != "None":
                persona.nickname = Key(nickname)
            else:
                persona.nickname = None

            photoKey = self.request.get("photo")
            if photoKey != "":
                photo = UserPhoto.get(photoKey)
                persona.picture = photo
            
            persona.put()

            generateVCard(persona)

            self.sendJsonOK()

        except datastore_errors.BadKeyError:
            raise AjaxError("Persona not found.")
            
            
    def setindividualpermit(self):

        itemKey = self.getRequiredParameter('key')
        canView = self.getRequiredBoolParameter('canview')
        
        try:
            individualPermit = IndividualPermit.get(itemKey)
            individualPermit.canView = canView
            individualPermit.put()
                  
            generateVCard(individualPermit.parent())
            
            self.sendJsonOK()
            
        except datastore_errors.BadKeyError:
            raise AjaxError("Individual permit not found.")
        
        
    def enablepublic(self):
        
        publicEnabled = self.getRequiredBoolParameter("enable")
        
        self.userProfile.publicEnabled = publicEnabled
        self.userProfile.put()
        
        self.sendJsonOK()


    def getvcardastext(self):
      
        persona = self._getPersonaUpdateVCard()
      
        self.response.headers['Content-Type'] = "text/x-vcard; charset=utf-8"
        self.response.headers['Content-Disposition'] = (u'inline; filename="' + persona.name + '.vcf"').encode("utf-8")
        self.response.out.write(persona.vcard)


    def getvcardasgif(self):

        persona = self._getPersonaUpdateVCard()
        
        qrcode = pyqrcode.MakeQRImage(persona.vcard.encode("utf-8"))

        output = StringIO.StringIO()
        qrcode.save(output, format="GIF")

        self.response.headers['Content-Type'] = "application/octet-stream"
        self.response.headers['Content-Disposition'] = (u'inline; filename="' + persona.name + '.gif"').encode("utf-8")
        self.response.out.write(output.getvalue())

        output.close()
        
        
#-----------------------------------------------------------------------------

class PersonaURLs(MasterHandler):

    def get(self, personaKey):

        if not self.getUserProfile():
            self.sendJsonError("User profile not found")

        try:
            persona = Persona.get(personaKey)
            
            friendsProfile = persona.parent()
            
            if contactExists(self.userProfile, friendsProfile):
                self.sendJsonError("Person already in contacts.")
            
            # Contact on user's side
            contact = Contact(parent = self.userProfile,
                              friend = friendsProfile,
                              group = self.userProfile.defaultGroup,
                              persona = self.userProfile.publicPersona)
            contact.put()

            # Contact on user's friend's side
            contact = Contact(parent = friendsProfile,
                              friend = self.userProfile,
                              group = friendsProfile.defaultGroup,
                              persona = persona)
            contact.put()
            
            self.sendContent("templates/Static_Success.html",
                              templateVariables = {
                                  'message': 'You have successfully added a new contact to your contact list',
            })
            
        except datastore_errors.BadKeyError:
            self.sendJsonError("Persona not found!")


#-----------------------------------------------------------------------------

app = webapp2.WSGIApplication([
    (r'/p/([a-zA-Z0-9\-]+)', PersonaURLs),
    (r'/personas/(\w+)', PersonasHandler),
], debug=True)
