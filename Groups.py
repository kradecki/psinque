# -*- coding: utf-8 -*-
import logging
import webapp2

from MasterHandler import MasterHandler, AjaxError
from users.UserDataModels import UserGroup, PermissionEmail

#-----------------------------------------------------------------------------

class GroupsHandler(MasterHandler):

    def get(self, actionName):
        
        if MasterHandler.safeGuard(self):
            
            actionFunction = getattr(self, actionName)
            
            try:
                actionFunction()
            except AjaxError as e:
                self.sendJsonError(e.value)

    def view(self):
        
        if MasterHandler.getUserProfile(self):
        
            userGroups = self.userProfile.groups
            
            MasterHandler.sendTopTemplate(self, activeEntry = "Groups")
            MasterHandler.sendContent(self, 'templates/groups_view.html', {
                'groups': userGroups,
            })
            MasterHandler.sendBottomTemplate(self)

    def removegroup(self):
        
        groupKey = self.checkGetParameter('key')
        userGroup = UserGroup.get(groupKey)
        
        if userGroup is None:
            raise AjaxError("Group not found")
        
        if userGroup.name == "Public":  # cannot remove the Public group
            raise AjaxError("Cannot remove the public group")

        for permissionEmail in userGroup.permissionEmails:
            permissionEmail.delete()
        userGroup.delete()

        self.sendJsonOK()
            
    def addgroup(self):
        
        groupName = self.checkGetParameter('name')

        if MasterHandler.getUserProfile(self):
            newGroup = UserGroup(parent = self.userProfile,
                                 creator = self.userProfile,
                                 name = groupName)
            newGroup.put()
            for email in self.userProfile.emails:
                permissionEmail = PermissionEmail(parent = newGroup,
                                                  userGroup = newGroup,
                                                  emailAddress = email)
                permissionEmail.put()
            self.sendJsonOK({"key": str(newGroup.key())});       
    
    def htmlBoolToPython(self, val):
        try:
            val = {"true": True, "false": False}[val]
            return val
        except KeyError:
            raise AjaxError("Unknown permission value: " + val);
    
    def setpermission(self):

        pkey = self.checkGetParameter('pkey')
        ptype = self.checkGetParameter('ptype')

        if ptype == "general":

            canViewName = self.htmlBoolToPython(self.checkGetParameter('canViewName'))
            canViewBirthday = self.htmlBoolToPython(self.checkGetParameter('canViewBirthday'))
            canViewGender = self.htmlBoolToPython(self.checkGetParameter('canViewGender'))
            
            userGroup = UserGroup.get(pkey)
            
            if userGroup is None:
                raise AjaxError("User group not found.")
            
            userGroup.canViewName = canViewName
            userGroup.canViewBirthday = canViewBirthday
            userGroup.canViewGender = canViewGender
            userGroup.put()
            
        elif ptype == "email":

            canView = self.htmlBoolToPython(self.checkGetParameter('canView'))
            
            permissionEmail = PermissionEmail.get(pkey)
            if permissionEmail is None:
                raise AjaxError("Email permission not found.")
            
            permissionEmail.canView = canView
            permissionEmail.put()
        
        else:
            raise AjaxError("Unknown permission type.")
        
        self.sendJsonOK()

#-----------------------------------------------------------------------------

app = webapp2.WSGIApplication([
    (r'/groups/(\w+)', GroupsHandler),
], debug=True)
