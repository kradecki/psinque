# -*- coding: utf-8 -*-

import logging
import webapp2

from MasterHandler import MasterHandler, AjaxError
from DataModels import Persona, Contact
from DataModels import IndividualPermit, PermitEmail, PermitIM, PermitPhoneNumber, PermitWebpage, PermitAddress

from DataManipulation import generateVCard

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

    #****************************
    # Views
    # 
    
    def view(self):
        
        if self.getUserProfile():
            
            self.sendContent('templates/Personas.html',
                            activeEntry = "Personas",
                            templateVariables = {
                'userProfile': self.userProfile,
                'personas': Persona.all(). \
                                  ancestor(self.userProfile). \
                                  order("name"),
            })


    #****************************
    # AJAX methods
    # 
    
    def removepersona(self):
        
        persona = Persona.get(self.getRequiredParameter('key'))
        
        # Check for errors
        if persona is None:
            raise AjaxError("Persona not found")
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
            
            
    def addpersona(self):
        
        personaName = self.getRequiredParameter('name')
        personaIndex = self.getRequiredParameter('index')
        
        # Error checking
        if personaName == "Public":
            raise AjaxError("Cannot create another public persona")
        if personaName == "Default":
            raise AjaxError("Cannot create another default private persona")

        # Check if the persona already exists
        persona = self._getPersonaByName(personaName)
        if not persona is None:
            raise AjaxError("Persona with that name already exists")

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
                'userProfile': self.userProfile,
                'personaIndex': personaIndex,
            })
    
    
    def setgeneral(self):

        persona = Persona.get(self.getRequiredParameter('key'))
        if persona is None:
            raise AjaxError("Persona not found.")

        persona.canViewGivenNames = self.getRequiredBoolParameter('givennames')
        persona.canViewFamilyNames = self.getRequiredBoolParameter('familynames')
        persona.canViewBirthday = self.getRequiredBoolParameter('birthday')
        persona.canViewGender = self.getRequiredBoolParameter('gender')
        persona.put()

        generateVCard(persona)

        self.sendJsonOK()
            
            
    def enablepublic(self):
        
        publicEnabled = self.getRequiredBoolParameter("enable")
        
        self.userProfile.publicEnabled = publicEnabled


    def setindividualpermit(self):

        itemKey = self.getRequiredParameter('key')
        canView = self.getRequiredBoolParameter('canview')
        
        individualPermit = IndividualPermit.get(itemKey)
        if individualPermit is None:
            raise AjaxError("Individual permit not found.")
        
        individualPermit.canView = canView
        individualPermit.put()
               
        generateVCard(individualPermit.parent())
        
        self.sendJsonOK()
        
        
#-----------------------------------------------------------------------------

app = webapp2.WSGIApplication([
    (r'/personas/(\w+)', PersonasHandler),
], debug=True)
