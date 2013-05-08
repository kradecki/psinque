# -*- coding: utf-8 -*-
import logging
import webapp2

from django.utils import simplejson as json

from MasterHandler import MasterHandler
from users.UserDataModels import UserGroup

#-----------------------------------------------------------------------------

class GroupsView(MasterHandler):
  
  def get(self):

    if MasterHandler.safeGuard(self) and MasterHandler.getUserProfile(self):
    
        userGroups = self.userProfile.groups
        
        MasterHandler.sendTopTemplate(self, activeEntry = "Groups")
        MasterHandler.sendContent(self, 'templates/groups_viewGroups.html', {
            'groups': userGroups,
        })
        MasterHandler.sendBottomTemplate(self)

#-----------------------------------------------------------------------------

class GroupsAction(MasterHandler):

    def get(self, actionName):
        
        if MasterHandler.safeGuard(self):
            actionFunction = getattr(self, actionName)
            actionFunction()

    def sendJsonOK(self):
        self.response.out.write(json.dumps({"status": 0}))

    def sendJsonError(self, msg):
        self.response.out.write(json.dumps({"status": 1,
                                            "message": msg}))

    def removegroup(self):
        
        group = UserGroup.get(self.request.get('key'))
        if group.name == "Public":  # cannot remove the Public group
            self.sendJsonError("Cannot remove the public group")
        else:
            group.delete()
            self.sendJsonOK()
            
    def addgroup(self):
        
        groupName = self.request.get('name')
        if groupName == "":
            self.sendJsonError("Empty group name.")
        elif MasterHandler.getUserProfile(self):
            newGroup = UserGroup(parent = self.userProfile,
                                    creator = self.userProfile,
                                    name = groupName)
            newGroup.put()
            self.response.out.write(json.dumps({"status": 0,
                                                "key": str(newGroup.key())}))
        
    def setpermission(self):

        groupKey = self.request.get("key")
        permissionType  = self.request.get("type")
        permissionName  = self.request.get("name")
        permissionValue = self.request.get("value")
        
        if (groupKey == "") or (permissionType == "") or (permissionName == "") or (permissionValue == ""):
            self.sendJsonError("All parameters are required.")
            return
        
        if permissionValue == "on":
            permissionValue = True
        elif permissionValue == "off":
            permissionValue = False
        else:
            self.sendJsonError("Unknown value.")
            return
        
        if MasterHandler.getUserProfile(self):
            
            userGroup = UserGroup.get(groupKey)
            
            if userGroup is None:
                self.sendJsonError("User group not found.")
                return
            
            if permissionType == "general":
                
                if permissionName == "canViewName":
                    userGroup.canViewName = permissionValue
                    self.sendJsonOK()
                elif permissionName == "canViewPsuedonym":
                    userGroup.canViewPsuedonym = permissionValue
                    self.sendJsonOK()
                elif permissionName == "canViewBirthday":
                    userGroup.canViewBirthday = permissionValue
                    self.sendJsonOK()
                elif permissionName == "canViewGender":
                    userGroup.canViewGender = permissionValue
                    self.sendJsonOK()
                else:
                    self.sendJsonError("Unknown permission name.")
                    return
                userGroup.put()
                
            elif permissionType == "mail":
                logging.info("Unimplemented.")
            
            else:
                self.sendJsonError("Unknown permission type.")
        
#-----------------------------------------------------------------------------

app = webapp2.WSGIApplication([
    (r'/groups', GroupsView),
    (r'/groups/(\w+)', GroupsAction),
], debug=True)
