
import os
import logging
import webapp2

from django.utils import simplejson as json

from MasterHandler import MasterHandler, AjaxError
from users.UserDataModels import UserProfile, Psinque, UserEmail, UserGroup
from users.UserManagement import getPublicGroup, getIncomingDisplayNameFromPsinque
from users.Email import notifyPendingPsinque

#-----------------------------------------------------------------------------

class PsinquesHandler(MasterHandler):

    def view(self):
        
        if self.getUserProfile():
            
            offset = self.request.get('offset')
            if not offset:
                offset = 0
            else:
                offset = int(offset)
            currentCursor = self.request.get('cursor')
            
            pendingPsinques = Psinque.all().filter("fromUser =", self.userProfile).filter("status =", "pending")
            pendingList = []
            for pending in pendingPsinques:
                pendingList.append({'name': getOutgoingDisplayNameFromPsinque(pending),
                                    'key': str(pending.key())})

            psinqueQuery = UserPsinque.all(keys_only = True).ancestor(self.userProfile).order("establishingTime")
            count = psinqueQuery.count(1000)
            contacts = []
            if currentCursor:
                psinqueQuery.with_cursor(currentCursor)  # start from the previous position
            for psinqueKey in psinqueQuery.run(limit=10):
                psinque = UserPsinque.get(psinqueKey)
                contacts.append({'nr': offset + len(contacts) + 1,
                                 'name': psinque.displayName,
                                 'date': psinque.establishingTime,
                                 'incomingType': psinque.incomingType,
                                 'outgoingType': psinque.outgoingType,
                                 'key': psinque.key(),
                                })
            template_values = {
                'offset': offset,
                'isThereMore': (offset + len(contacts) < count),
                'count': count,
                'nextCursor': psinqueQuery.cursor(),
                'contacts': contacts,
                'pendings': pendingList,
                'groups': UserGroup.all().ancestor(self.userProfile),
            }
                    
            MasterHandler.sendTopTemplate(self, activeEntry = "Psinques")
            MasterHandler.sendContent(self, 'templates/psinques_view.html', template_values)
            MasterHandler.sendBottomTemplate(self)

    def searchemail(self):

        email = self.request.get('email')
        userEmail = UserEmail.all(keys_only = True).filter("email =", email).get()
        if userEmail:
            userID = userEmail.parent().id()
            if MasterHandler.getUserProfile(self):            
                psinque = Psinque.all(keys_only = True).ancestor(self.userProfile).filter("fromUser =", userEmail.parent()).get()
                if psinque:
                    self.response.out.write(json.dumps({"status": 1})) # psinque already exists
                else:
                    self.response.out.write(json.dumps({"status": 0, "fromUser": userID}))
        else:
            self.response.out.write(json.dumps({"status": -1}))   # user not found


    def addincoming(self):
        
        if MasterHandler.getUserProfile(self):
            
            fromUser = UserProfile.get_by_id(int(self.request.get('from')))  # get user by key
            
            incomingType = self.request.get('type')
            if incomingType == "public":
                newPsinque = Psinque(parent = self.userProfile, toUser = self.userProfile,
                                    fromUser = fromUser,
                                    status = "established",
                                    group = getPublicGroup(fromUser))
                newPsinque.put()
                self.redirect('/psniques')
                
            elif incomingType == "private":
                newPsinque = Psinque(parent = self.userProfile, toUser = self.userProfile,
                                    fromUser = fromUser,
                                    status = "pending")
                newPsinque.put()
                notifyPendingPsinque(newPsinque)
                self.response.out.write(json.dumps({"status": 0}))
                
            else:
                self.response.out.write(json.dumps({"status": 1}))

   
    def _removeIfEmptyContact(self, contact):
        if (contact.incoming is None) and (contact.outgoing is None):
            for contactGroup in contact.contactGroups:
                contactGroup.delete()
            contact.delete()

    def _getContact(self):

        if not MasterHandler.getUserProfile(self):
            self.sendJsonError("User not logged in")
            return None

        # Find contact on this end
        contact = Contact.get(self.checkGetParameter('key'))
        if contact is None:
            self.sendJsonError("Contact not found")
            return None
            
        if contact.parent() != self.userProfile:
            self.sendJsonError("You cannot modify contacts that do not belong to you")
            return None
        
        return contact


    def removeincoming(self):
        
        contact = self._getContact()
        if is contact None:
            return
        
        # Contact on the other end of this psinque
        psinque = contact.incoming
        friendsContact = Contact.all(keys_only = True).
                                     filter("outgoing =", psinque.key()).
                                     get()
        
        # Remove psinque from my contact
        contact.incoming = None
        self._removeIfEmptyContact(contact)

        # Remove psinque from my friend's contact
        friendsContact.outgoing = None
        self._removeIfEmptyContact(friendsContact)

        # Remove psinque
        psinque.delete()
        
        self.sendJsonOK()

    def removeoutgoing(self):
        
        contact = self._getContact()
        if is contact None:
            return
        
        # Contact on the other end of this psinque
        psinque = contact.incoming
        
        # Remove psinque from my contact
        contact.outgoing = None
        self._removeIfEmptyContact(contact)
        
        # Downgrade psinque to public
        psinque.
        
        self.sendJsonOK()

    def removecontact(self):
        
        contact = Contact.get(self.checkGetParameter('key'))
        if not contact is None:
            psinque = contact.incoming
            psinque.delete()
            psinque = contact.outgoing
            psinque.delete()
            contact.delete()
        self.sendJsonOK()
                       

    def upgradeincoming(self):
        

    def viewdecision(self):
        
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
            raise AjaxError("Psinque not found.")
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

    
    def acceptrequest(self):
        
        psinque = self.getPsinqueByKey()
        psinque.status = "established"
        psinque.put()
        self.sendJsonOK()
    
    
    def rejectrequest(self):
        
        psinque = self.getPsinqueByKey()
        psinque.status = "rejected"
        psinque.put()
        self.sendJsonOK()

#-----------------------------------------------------------------------------

app = webapp2.WSGIApplication([
    (r'/psinques/(\w+)', PsinquesHandler),
    #(r'/decisions/(\w+)', OutgoingDecisions),
], debug=True)
