# -*- coding: utf-8 -*-

import logging
import webapp2

from MasterHandler import MasterHandler, AjaxError
from DataModels import Permit, Contact, generateVCard
from DataModels import IndividualPermit, PermitEmail, PermitIM, PermitPhoneNumber, PermitWebpage, PermitAddress

#-----------------------------------------------------------------------------

class PermitsHandler(MasterHandler):

    #****************************
    # Private methods
    # 
    
    def _getPermitByName(self, permitName):
        return Permit.all(). \
                      ancestor(self.userProfile). \
                      filter("name =", permitName). \
                      get()

    #****************************
    # Views
    # 
    
    def view(self):
        
        if self.getUserProfile():
            
            self.sendContent('templates/Permits.html',
                            activeEntry = "Permits",
                            templateVariables = {
                'userProfile': self.userProfile,
                'permits': Permit.all(). \
                                  ancestor(self.userProfile). \
                                  order("name"),
            })


    #****************************
    # AJAX methods
    # 
    
    def removepermit(self):
        
        permit = Permit.get(self.getRequiredParameter('key'))
        
        # Check for errors
        if permit is None:
            raise AjaxError("Permit not found")
        if permit.name == "Public":  # cannot remove the public permit
            raise AjaxError("Cannot remove the public permit")
        if permit.name == "Default":  # cannot remove the default permit
            raise AjaxError("Cannot remove the default private permit")

        # Get all contacts that use this permit and assign them the default permit
        contacts = Contact.all(). \
                           ancestor(self.userProfile). \
                           filter("permit =", permit)
        defaultPermit = self._getPermitByName("Default")
        for contact in contacts:
            contact.permit = defaultPermit

        # Remove all children individual permits
        individualPermits = IndividualPermit.all().ancestor(permit)
        for individualPermit in individualPermits:
            individualPermit.delete()
        permit.delete()  # and the permit itself

        self.sendJsonOK()
            
            
    def addpermit(self):
        
        permitName = self.getRequiredParameter('name')
        permitIndex = self.getRequiredParameter('index')
        
        # Error checking
        if permitName == "Public":
            raise AjaxError("Cannot create another public permit")
        if permitName == "Default":
            raise AjaxError("Cannot create another default private permit")

        # Check if the permit already exists
        permit = self._getPermitByName(permitName)
        if not permit is None:
            raise AjaxError("Permit with that name already exists")

        # Create a new Permit
        newPermit = Permit(parent = self.userProfile,
                           name = permitName)
        newPermit.put()
        
        for email in self.userProfile.emails:
            permitEmail = PermitEmail(parent = newPermit,
                                      userEmail = email)
            permitEmail.put()
            
        for im in self.userProfile.ims:
            permitIM = PermitIM(parent = newPermit,
                                userIM = im)
            permitIM.put()
            
        for www in self.userProfile.webpages:
            permitWebpage = PermitWebpage(parent = newPermit,
                                          userWebpage = www)
            permitWebpage.put()
            
        for phone in self.userProfile.phones:
            permitPhoneNumber = PermitPhoneNumber(parent = newPermit,
                                                  userPhoneNumber = phone)
            permitPhoneNumber.put()
            
        for address in self.userProfile.addresses:
            permitAddress = PermitAddress(parent = newPermit,
                                          userAddress = address)
            permitAddress.put()
        
        # Generate the Permit's vCard and eTag:
        generateVCard(newPermit)

        self.sendContent('templates/Permits_Permit.html',
                         activeEntry = "Permits",
                         templateVariables = {
                'permit': newPermit,
                'userProfile': self.userProfile,
                'permitIndex': permitIndex,
            })
    
    
    def setgeneralpermit(self):

        permit = Permit.get(self.getRequiredParameter('key'))
        if permit is None:
            raise AjaxError("Permit not found.")

        permit.canViewGivenNames = self.getRequiredBoolParameter('givennames')
        permit.canViewFamilyNames = self.getRequiredBoolParameter('familynames')
        permit.canViewBirthday = self.getRequiredBoolParameter('birthday')
        permit.canViewGender = self.getRequiredBoolParameter('gender')
        permit.put()

        generateVCard(permit)

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
    (r'/permits/(\w+)', PermitsHandler),
], debug=True)
