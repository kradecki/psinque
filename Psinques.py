
import os
import logging
import webapp2

from django.utils import simplejson as json

from MasterHandler import MasterHandler, AjaxError
from Notifications import notifyPendingPsinque
from Permits import Permit

#-----------------------------------------------------------------------------
# Data models

class Psinque(db.Model):
    
    fromUser = db.ReferenceProperty(UserProfile,
                                    collection_name = "outgoing")
    toUser   = db.ReferenceProperty(UserProfile,
                                    collection_name = "incoming")
    
    status = db.StringProperty(choices = ["pending", "established", "rejected", "banned"])
    private = db.BooleanProperty()

    creationTime = db.DateTimeProperty(auto_now = True)
  
class Contact(db.Model):

    incoming = db.ReferenceProperty(Psinque)
    incomingPrivate = db.BooleanProperty()
    incomingPending = db.BooleanProperty()

    outgoing = db.ReferenceProperty(Psinque)
    outgoingPrivate = db.BooleanProperty()
    outgoingPending = db.BooleanProperty()

    friend = db.ReferenceProperty(UserProfile)
    
    group = db.ReferenceProperty(Group)
    permit = db.ReferenceProperty(Permit)

    displayName = db.StringProperty()
    creationTime = db.DateTimeProperty(auto_now = True)

class Group(db.Model):
    
    name = db.StringProperty()
    sync = db.BooleanProperty(default = True)

#-----------------------------------------------------------------------------
# Request handler

class PsinquesHandler(MasterHandler):

    def _getPrimaryEmail(user):
        return user.emails.ancestor(user.key()).filter("primary =", True).get().email


    def _getPublicGroup(user):
        publicGroup = UserGroup.all(keys_only = True)
        publicGroup.ancestor(user.key())
        publicGroup.filter("name =", "Public")
        return publicGroup.get()


    #def _getIncomingDisplayNameFromPsinque(psinque):
        #publicGroupKey = _getPublicGroup(psinque.fromUser)
        #if UserGroup.get(publicGroupKey).canViewName:
            #return getName(psinque.fromUser)
        #for group in psinque.groups:
            #if group and group.canViewName:
                #return getName(psinque.fromUser)
        #return _getPrimaryEmail(psinque.fromUser)


    def _getOutgoingDisplayNameFromPsinque(psinque):
        publicGroupKey = _getPublicGroup(psinque.toUser)
        if UserGroup.get(publicGroupKey).canViewName:
            return getName(psinque.toUser)
        for group in psinque.groups:
            if group and group.canViewName:
                return getName(psinque.toUser)
        return _getPrimaryEmail(psinque.toUser)


    #def _getDisplayName(user, toUser):
        
        #if not _getPublicGroup(fromUser).canViewName: # Perhaps the name is visible to everyone?  
            #psinque = Psinque.all().filter("toUser =", toUser).filter("fromUser =", user).get()
            #primaryEmail = _getPrimaryEmail(user)
            #if (len(psinque) == 0) or (psinque.status != "Established") or (not psinque.group.canViewName):
                #return primaryEmail    # email address is always visible
        #return getName(user)

    def _removeIfEmptyContact(self, contact):
        if (contact.incoming is None) and (contact.outgoing is None):
            for contactGroup in contact.contactGroups:
                contactGroup.delete()
            contact.delete()

    def _getContact(self):

        if not self.getUserProfile():
            raise AjaxError("User not logged in")

        # Find contact on this end
        contact = Contact.get(self.checkGetParameter('key'))
        if contact is None:
            raise AjaxError("Contact not found")
            
        if contact.parent() != self.userProfile:
            raise AjaxError("You cannot modify contacts that do not belong to you")
        
        return contact


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
                pendingList.append({'name': _getOutgoingDisplayNameFromPsinque(pending),
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
                    
            self.sendTopTemplate( activeEntry = "Psinques")
            self.sendContent('templates/psinques_view.html', {
                'offset': offset,
                'isThereMore': (offset + len(contacts) < count),
                'count': count,
                'nextCursor': psinqueQuery.cursor(),
                'contacts': contacts,
                'pendings': pendingList,
                'groups': UserGroup.all().ancestor(self.userProfile),
            })
            self.sendBottomTemplate()

    def searchemail(self):

        # Search for the owner of the email address
        email = self.request.get('email')
        userEmail = UserEmail.all(keys_only = True).filter("email =", email).get()

        if not userEmail:
            raise AjaxError("User not found")
        if not self.getUserProfile():
            raise AjaxError("User profile not found")
        
        # Check if there already is a Psinque from that user
        userProfile = userEmail.parent()
        psinque = Psinque.all(keys_only = True).ancestor(self.userProfile).filter("fromUser =", userProfile).get()
        if psinque:
            raise AjaxError("Psinque already exists")
        
        self.sendJsonOK({
            "key": userProfile.key(),
            "publicEnabled": userProfile
        })


    def requestprivate(self):
        
        if not self.getUserProfile():
            raise AjaxError("User profile not found")
            
        contact = Contact.get(self.request.get('key'))
        
        newPsinque = Psinque(parent = contact,
                             private = False,
                             toUser = self.userProfile,
                             fromUser = contact.parent(),
                             status = "pending")
        newPsinque.put()


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
