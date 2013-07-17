# -*- coding: utf-8 -*-

import logging
import webapp2

from MasterHandler import MasterHandler, AjaxError
from DataModels import Permit, PermitEmail, Contact

#-----------------------------------------------------------------------------

class PermitsHandler(MasterHandler):

    #****************************
    # Private methods
    # 
    
    def _getPermitByName(self, permitName):
        return Permit.all().ancestor(self.userProfile).filter("name =", permitName).get()

    #****************************
    # Views
    # 
    
    def view(self):
        
        if self.getUserProfile():
            
            permits = Permit.all().ancestor(self.userProfile)
            
            self.sendContent('templates/Permits.html',
                            activeEntry = "Permits",
                            templateVariables = {
                'userProfile': self.userProfile,
                'permits': permits,
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
        contacts = Contact.all().ancestor(self.userProfile).filter("permit =", permit)
        defaultPermit = self._getPermitByName("Default")
        for contact in contacts:
            contact.permit = defaultPermit

        # Remove all children
        permitEmails = PermitEmail.all().ancestor(permit)
        for permitEmail in permitEmails:
            permitEmail.delete()
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
        
        # Generate the Permit's vCard and eTag:
        newPermit.generateVCard()
        newPermit.put()
        logging.info("New permit created, key = " + str(newPermit.key()))

        self.sendContent('templates/Permits_Permit.html',
                         activeEntry = "Permits",
                         templateVariables = {
                'permit': newPermit,
                'userProfile': self.userProfile,
                'permitIndex': permitIndex,
            })
    
    
    def setgeneralpermit(self):

        pkey = self.getRequiredParameter('key')

        canViewFirstNames = self.getRequiredBoolParameter('firstnames')
        canViewLastNames = self.getRequiredBoolParameter('lastnames')
        canViewBirthday = self.getRequiredBoolParameter('birthday')
        canViewGender = self.getRequiredBoolParameter('gender')
        
        permit = Permit.get(pkey)
        if permit is None:
            raise AjaxError("Permit not found.")
        
        permit.canViewFirstNames = canViewFirstNames
        permit.canViewLastNames = canViewLastNames
        permit.canViewBirthday = canViewBirthday
        permit.canViewGender = canViewGender
        permit.put()  # it doesn't work without this line, don't ask me why
        permit.generateVCard()
        permit.put()

        self.sendJsonOK()
            
    def setemailpermit(self):

        pkey = self.getRequiredParameter('key')
        canView = self.getRequiredBoolParameter('canview')
        
        permitEmail = PermitEmail.get(pkey)
        if permitEmail is None:
            raise AjaxError("Email permit not found.")
        
        permitEmail.canView = canView
        permitEmail.put()
               
        permitEmail.parent().generateVCard()
        permitEmail.parent().put()
        
        self.sendJsonOK()
        
        
    def enablepublic(self):
        
        publicEnabled = self.getRequiredBoolParameter("enable")
        
        self.userProfile.publicEnabled = publicEnabled

#-----------------------------------------------------------------------------

app = webapp2.WSGIApplication([
    (r'/permits/(\w+)', PermitsHandler),
], debug=True)
