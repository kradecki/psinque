# -*- coding: utf-8 -*-
import logging
import webapp2

from vobject import vCard
from datetime import datetime
import md5

from MasterHandler import MasterHandler, AjaxError
from Psinques import Contact

#-----------------------------------------------------------------------------
# Data models

class Permit(db.Model):
    
    name = db.StringProperty()
    public = db.BooleanProperty(default = False)

    canViewName = db.BooleanProperty(default = True)
    canViewBirthday = db.BooleanProperty(default = False)
    canViewGender = db.BooleanProperty(default = False)

    vcard = db.Text()   # vCard for CardDAV access; it's not a StringProperty
                        # because it might be longer than 500 characters
    vcardMTime = db.StringProperty() # modification time
    vcardMD5 = db.StringProperty()   # MD5 checksum of the vcard
    
    def generateVCard(self):
        
        userProfile = Permit.parent()
        newVCard = vCard()
        newVCard.add('n')
        newVCard.n.value = userProfile.name
        newVCard.add('fn')
        newVCard.fn.value = userProfile.fullName
        if userProfile.companyName:
            newVCard.add('org')
            newVCard.org.value = userProfile.companyName
        for email in userProfile.emails:
            newVCard.add('email')
            newVCard.email.value = email.email
            newVCard.email.type_param = email.emailType  #TODO: convert to vCard type names?
        
        Permit.vcard = newVCard.serialize()
        Permit.vcardMTime = str(datetime.date(datetime.now())) + "-" + str(datetime.time(datetime.now()))
        Permit.vcardMD5 = md5.new(Permit.vcard).hexdigest()


class PermitEmail(db.Model):

    userEmail = db.ReferenceProperty(UserEmail,
                                     collection_name = "permitEmails")
    canView = db.BooleanProperty(default = False)
    
#-----------------------------------------------------------------------------
# Request handler

class PermitsHandler(MasterHandler):

    #****************************
    # Private methods
    # 
    
    def _getPermitByName(self, permitName):
        return Permit.all().ancestor(self.userProfile).filter("name =", "Default").get()

    #****************************
    # Views
    # 
    
    def view(self):
        
        if self.getUserProfile():
        
            permits = Permit.all().ancestor(self.userProfile)
            
            self.sendTopTemplate(activeEntry = "Groups")
            self.sendContent('templates/permits_view.html', {
                'groups': permits,
            })
            self.sendBottomTemplate()


    #****************************
    # AJAX methods
    # 
    
    def removepermit(self):
        
        permit = Permit.get(self.getRequiredParameter('key'))
        
        # Check for errors
        if permit is None:
            raise AjaxError("Group not found")
        if permit.name == "Public":  # cannot remove the public group
            raise AjaxError("Cannot remove the public group")
        if permit.name == "Default":  # cannot remove the default group
            raise AjaxError("Cannot remove the default private group")
        if not self.getUserProfile():
            raise AjaxError("User profile not found")

        # Get all contacts that use this permit and assign them the default permit
        contacts = Contact.all().ancestor(self.userProfile).filter("permit =", permit)
        defaultPermit = self._getPermitByName("Default")
        for contact in contacts:
            contact.permit = defaultPermit

        # Remove all children
        permitEmails = PermitEmails.all(keys_only = True).ancestor(permit)
        for permitEmail in permitEmails:
            permitEmail.delete()
        permit.delete()  # and the permit itself

        self.sendJsonOK()
            
            
    def addpermit(self):
        
        permitName = self.getRequiredParameter('name')
        
        # Error checking
        if permitName == "Public":
            raise AjaxError("Cannot create another public group")
        if permitName == "Default":
            raise AjaxError("Cannot create another default private group")
        if not self.getUserProfile():
            raise AjaxError("User profile not found")

        # Check if the permit already exists
        permit = self._getPermitByName(permitName)
        if not permit is None:
            raise AjaxError("Group with that name already exists")

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
        
        self.sendJsonOK({"key": str(newPermit.key())});       
    
    
    def setpermit(self):

        pkey = self.getRequiredParameter('key')
        ptype = self.getRequiredParameter('type')

        if ptype == "general":

            canViewName = self.getRequiredBoolParameter('canViewName')
            canViewBirthday = self.getRequiredBoolParameter('canViewBirthday')
            canViewGender = self.getRequiredBoolParameter('canViewGender')
            
            userGroup = UserGroup.get(pkey)
            
            if userGroup is None:
                raise AjaxError("User group not found.")
            
            userGroup.canViewName = canViewName
            userGroup.canViewBirthday = canViewBirthday
            userGroup.canViewGender = canViewGender
            userGroup.put()
            
        elif ptype == "email":

            canView = self.getRequiredBoolParameter('canView')
            
            permissionEmail = PermissionEmail.get(pkey)
            if permissionEmail is None:
                raise AjaxError("Email permission not found.")
            
            permissionEmail.canView = canView
            permissionEmail.put()
        
        else:
            raise AjaxError("Unknown permission type.")
        
        # Re-generate the Permit's vCard and eTag:
        newPermit.generateVCard()
        
        self.sendJsonOK()
        
        
    def enablepublic(self):
        
        publicEnabled = self.getRequiredBoolParameter("enable")
        if not self.getUserProfile():
            raise AjaxError("User profile not found")
        
        self.userProfile.publicEnabled = publicEnabled

#-----------------------------------------------------------------------------

app = webapp2.WSGIApplication([
    (r'/permits/(\w+)', PermitsHandler),
], debug=True)
