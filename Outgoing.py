
import os
import logging
import webapp2

from google.appengine.ext.db import BadKeyError

from django.utils import simplejson as json

from MasterHandler import MasterHandler, AjaxError
from users.UserDataModels import UserProfile, Psinque, UserEmail, UserGroup, PsinqueGroup
from users.UserManagement import getPublicGroup, getOutgoingDisplayNameFromPsinque
from users.Email import notifyPendingPsinque

#-----------------------------------------------------------------------------

class OutgoingHandler(MasterHandler):

    def get(self, actionName):
        
        if MasterHandler.safeGuard(self):
            
            actionFunction = getattr(self, actionName)
            
            try:
                actionFunction()
            except AjaxError as e:
                self.sendJsonError(e.value)

    def view(self):
    
        if self.getUserProfile():
            pendingPsinques = Psinque.all().filter("fromUser =", self.userProfile).filter("status =", "pending")

            pendingList = []
            for pending in pendingPsinques:
                pendingList.append({'name': getOutgoingDisplayNameFromPsinque(pending),
                                    'key': str(pending.key())})

            template_values = {
                'pendings': pendingList,
                'groups': UserGroup.all().ancestor(self.userProfile),
            }

            MasterHandler.sendTopTemplate(self, activeEntry = "Outgoing")
            MasterHandler.sendContent(self, 'templates/outgoing_view.html', template_values)
            MasterHandler.sendBottomTemplate(self)
                
#-----------------------------------------------------------------------------

class OutgoingDecisions(MasterHandler):
    
    def get(self, actionName):
        
        actionFunction = getattr(self, actionName)
        try:
            actionFunction()
        except AjaxError as e:
            self.sendJsonError(e.value)
        except BadKeyError:
            self.sendJsonError("Entity not found.")
                

    def view(self):
        
        self.sendTopTemplate(self, activeEntry = "Outgoing")
        decisionKey = self.response.get('key')
        decision = PendingDecision.get(decisionKey)
        if decision is None:
            self.sendContent(self, 'templates/outgoing_error.html', {
                'message': "Pending decision not found. Are you sure you have not resolved it already?",
            })
        else:
            self.sendContent(self, 'templates/outgoing_decision.html', {
                'decision': decision,
            })
        self.sendBottomTemplate(self)


    def getPsinqueByKey(self):
        psinqueKey = self.checkGetParameter('key')
        psinque = Psinque.get(psinqueKey)
        if psinque is None:
            raise AjaxError("Pending decision not found.")
        return psinque
    
    
    def addtogroup(self):

        psinque = self.getPsinqueByKey()
        userProfile = psinque.fromUser
        groupName = self.checkGetParameter('group')
        group = UserGroup.all(keys_only = True).filter("name =", groupName).get()
        if group is None:
            raise AjaxError("Group " + groupName + " does not exist.")
        
        # First we check if this psinque is not already asigned to that group
        psinqueGroup = PsinqueGroup.all(keys_only = True).ancestor(psinque).filter("group =", group).get()
        if psinqueGroup is None:
            psinqueGroup = PsinqueGroup(parent = psinque,
                                        psinque = psinque,
                                        group = group)
            psinqueGroup.put()
        self.sendJsonOK()

    
    def accept(self):
        psinque = self.getPsinqueByKey()
        psinque.status = "established"
        psinque.put()
        self.sendJsonOK()
    
    
    def reject(self):
        psinque = self.getPsinqueByKey()
        psinque.status = "rejected"
        psinque.put()
        self.sendJsonOK()

#-----------------------------------------------------------------------------

app = webapp2.WSGIApplication([
    (r'/outgoing/(\w+)', OutgoingHandler),
    (r'/decisions/(\w+)', OutgoingDecisions),
], debug=True)
