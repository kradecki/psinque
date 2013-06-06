
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
    #toUser   = db.ReferenceProperty(UserProfile,
                                    #collection_name = "incoming")
    
    status = db.StringProperty(choices = ["pending", "established", "banned"])
    private = db.BooleanProperty(default = False)

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

    #****************************
    # Private methods
    # 
    
    def _getPrimaryEmail(user):
        return user.emails.ancestor(user.key()).filter("primary =", True).get().email


    #def _getPublicGroup(user):
        #publicGroup = UserGroup.all(keys_only = True)
        #publicGroup.ancestor(user.key())
        #publicGroup.filter("name =", "Public")
        #return publicGroup.get()


    #def _getIncomingDisplayNameFromPsinque(psinque):
        #publicGroupKey = _getPublicGroup(psinque.fromUser)
        #if UserGroup.get(publicGroupKey).canViewName:
            #return getName(psinque.fromUser)
        #for group in psinque.groups:
            #if group and group.canViewName:
                #return getName(psinque.fromUser)
        #return _getPrimaryEmail(psinque.fromUser)


    #def _getOutgoingDisplayNameFromPsinque(psinque):
        #publicGroupKey = _getPublicGroup(psinque.toUser)
        #if UserGroup.get(publicGroupKey).canViewName:
            #return getName(psinque.toUser)
        #for group in psinque.groups:
            #if group and group.canViewName:
                #return getName(psinque.toUser)
        #return _getPrimaryEmail(psinque.toUser)


    #def _getDisplayName(user, toUser):
        
        #if not _getPublicGroup(fromUser).canViewName: # Perhaps the name is visible to everyone?  
            #psinque = Psinque.all().filter("toUser =", toUser).filter("fromUser =", user).get()
            #primaryEmail = _getPrimaryEmail(user)
            #if (len(psinque) == 0) or (psinque.status != "Established") or (not psinque.group.canViewName):
                #return primaryEmail    # email address is always visible
        #return getName(user)


    def _getContact(self):

        if not self.getUserProfile():
            raise AjaxError("User not logged in")

        # Find contact on this end
        contact = Contact.get(self.getRequiredParameter('key'))
        if contact is None:
            raise AjaxError("Contact not found")
            
        if contact.parent() != self.userProfile:
            raise AjaxError("You cannot modify contacts that do not belong to you")
        
        return contact
    
    
    def _getContactForOutgoing(self, psinque):
        '''
        Finds and returns a Contact that has the "psinque" in the 
        "outgoing" field. This Contact will belong to an unknown
        user, so we cannot use ancestor queries.
        '''
        return Contact.all(keys_only = True).
                       ancestor(psinque.fromUser).
                       filter("outgoing =", psinque).
                       get()

    def _getContactForIncoming(self, psinque):
        '''
        Finds and returns a Contact that has the "psinque" in the 
        "incoming" field. This Contact is in fact the parent of this
        Psinque.
        '''
        return psinque.parent()


    def _clearIncoming(self, contact):
        contact.incoming = None
        if contact.outgoing is None:
            contact.delete()


    def _clearOutgoing(self, contact):
        contact.outgoing = None
        if contact.incoming is None:
            contact.delete()


    def _removeIncoming(self, contact):
        '''
        Removes the incoming Psinque from a Contact. If the Contact
        is empty, it is removed. This Psinque is also removed from
        the friend's Contact. The Psinque is removed as well.
        '''
        psinque = contact.incoming
        friendsContact = self._getContactForOutgoing(psinque)
        self._clearIncoming(contact)
        self._clearOutgoing(friendsContact)
        psinque.delete()
        Notifications.notifyStoppedUsingPrivateData(psinque)


    def _removeOutgoing(self, contact):
        '''
        Removes the outgoing Psinque from a Contact. If the Contact
        is empty, it is removed. The Psinque is then downgraded to
        a public psinque, so it's not removed from the friend's
        Contact.
        '''
        psinque = contact.outgoing        
        self._clearOutgoing(contact)
        psinque.private = False
        Notifications.notifyDowngradedPsinque(psinque)


    def _getPsinqueByKey(self):
        
        if not self.getUserProfile():
            raise AjaxError("User profile not found")
        
        psinqueKey = self.getRequiredParameter('key')
        psinque = Psinque.get(psinqueKey)
        if psinque is None:
            raise AjaxError("Psinque not found.")
        return psinque

    
    def _getPsinqueFrom(self):
        return Psinque.all(keys_only = True).
                       ancestor(self.userProfile).
                       filter("fromUser =", userProfile).
                       get()
    
    
    def _addRequestToUpgrade(self, contact):

        if contact.incoming.private:
            raise AjaxError("You already have access to private data")
            
        newPsinque = Psinque(parent = contact,
                             private = True,
                             fromUser = contact.parent(),
                             status = "pending")
        newPsinque.put()
        Notifications.notifyPendingPsinque(newPsinque)
    
    
    def _addPublicPsinque(self, friendsProfile):
        
        if not self.getUserProfile():
            raise AjaxError("User not logged in")

        newContact = Contact(parent = self.userProfile,
                             friend = friendsProfile,
                             group = self.userProfile.defaultGroup,
                             permit = self.userProfile.publicPermit)
        newContact.put()
        
        newPsinque = Psinque(parent = newContact,
                             fromUser = friendsProfile,
                             private = False,
                             permit = friendsProfile.defaultPermit,
                             status = "established")
        newPsinque.put()
        
        return newPsinque
        

    #****************************
    # Views
    # 
    
    def view(self):
        
        if self.getUserProfile():
                        
            offset = self.request.get('offset')
            if not offset:
                offset = 0
            else:
                offset = int(offset)
            currentCursor = self.request.get('cursor')
            
            # Pending decisions
            pendingPsinques = Psinque.all().filter("fromUser =", self.userProfile).filter("status =", "pending")
            pendingList = []
            for pending in pendingPsinques:
                pendingList.append({'name': _getOutgoingDisplayNameFromPsinque(pending),
                                    'key': str(pending.key())})

            # List of contacts
            contactQuery = Contact.all(keys_only = True).
                                   ancestor(self.userProfile).
                                   order("establishingTime")
            count = contactQuery.count(1000)
            if currentCursor:
                contactQuery.with_cursor(currentCursor)  # start from the previous position
            contacts = contactQuery.run(limit = 10)
            
            if len(contacts) == 10:
                isThereMore = (offset + 10 < count)
            else:
                isThereMore = False
                    
            self.sendTopTemplate(activeEntry = "Psinques")
            self.sendContent('templates/psinques_view.html', {
                'offset': offset,
                'isThereMore': (offset + len(contacts) < count),
                'count': count,
                'nextCursor': contactQuery.cursor(),
                'contacts': contacts,
                'pendings': pendingList,
                'groups': Group.all().ancestor(self.userProfile),
                'permits': Permit.all().ancestor(self.userProfile),
            })
            self.sendBottomTemplate()


    #def viewdecision(self):
        
        #self.sendTopTemplate(self, activeEntry = "Outgoing")
        #decisionKey = self.response.get('key')
        #decision = PendingDecision.get(decisionKey)
        #if decision is None:
            #self.sendContent(self, 'templates/outgoing_error.html', {
                #'message': "Pending decision not found. Are you sure you have not resolved it already?",
            #})
        #else:
            #self.sendContent(self, 'templates/outgoing_decision.html', {
                #'decision': decision,
            #})
        #self.sendBottomTemplate(self)

    
    #****************************
    # AJAX methods
    # 
    
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
        psinque = self._getPsinqueFrom(userProfile)
        if psinque:
            raise AjaxError("Psinque already exists")
        
        self.sendJsonOK({
            "key": userProfile.key(),
            "publicEnabled": userProfile.publicEnabled,
        })


    def requestupgrade(self):
        
        contact = self._getContact()     
        self._addRequestToUpgrade(contact)
        self.sendJsonOK()
    

    def addpublic(self):
                
        friendsProfile = UserProfile.get(getRequiredParameter("key"))

        psinque = self._getPsinqueFrom(friendsProfile)
        if psinque:
            raise AjaxError("You already have this psinque")
        
        self._addPublicPsinque(friendsProfile)


    def addprivate(self):
        
        if not self.getUserProfile():
            raise AjaxError("User not logged in")
        
        friendsProfile = UserProfile.get(getRequiredParameter("key"))
        psinque = self._getPsinqueFrom(friendsProfile)
        if psinque:
            if psinque.private:
                raise AjaxError("You already have this psinque")
            else:
                self._addRequestToUpgrade(psinque.parent())
        else:
            newPsinque = self._addPublicPsinque(friendsProfile)
            self._addRequestToUpgrade(newPsinque.parent())


    def removeincoming(self):
        
        contact = self._getContact()
        self._removeIncoming(contact)        
        self.sendJsonOK()


    def removeoutgoing(self):
        
        contact = self._getContact()       
        self._removeOutgoing(contact)
        self.sendJsonOK()


    def removecontact(self):
        
        contact = self._getContact()
        self._removeIncoming(contact)
        self._removeOutgoing(contact)
        self.sendJsonOK()
                       

    def changepermit(self):

        contact = Contact.get(self.getRequiredParameter('contact'))
        if not contact:
            raise AjaxError("Contact does not exist")

        permit  = Permit.get(self.getRequiredParameter('permit'))
        if not permit:
            raise AjaxError("Permit does not exist")
        
        # First we check if this psinque is not already asigned to that group
        contact.permit = permit
        contact.put()
            
        self.sendJsonOK()


    def changegroup(self):
        
        raise AjaxError("Unimplemented")

    
    def acceptrequest(self):
        
        psinque = self._getPsinqueByKey()
        #TODO: check for userProfile
        
        contactIn = self._getContactForIncoming(psinque)
        contactOut = self._getContactForOutgoing(psinque)
        
        if contactOut.outgoing:
            raise AjaxError("There already is a psinque from this user")
        
        existingPsinque = contactIn.incoming
        if existingPsinque:
            if existingPsinque.private:
                psinque.delete()
                raise AjaxError("There already is a private psinque from this user")
            else:
                existingPsinque.delete()
                    
        contactIn.incoming = psinque
        contactIn.put()
        
        contactOut.outgoing = psinque
        contactOut.put()
        
        psinque.status = "established"
        psinque.permit = psinque.fromUser.defaultPermit
        psinque.put()
        
        Notifications.notifyAcceptedRequest(psinque)
        
        self.sendJsonOK()
    
    
    def rejectrequest(self):
        
        psinque = self._getPsinqueByKey()       
        psinque.delete()

        Notifications.notifyRejectedRequest(psinque)
        
        self.sendJsonOK()


    def banrequest(self):
        
        raise AjaxError("Unimplemented")
        
#-----------------------------------------------------------------------------

app = webapp2.WSGIApplication([
    (r'/psinques/(\w+)', PsinquesHandler),
    #(r'/decisions/(\w+)', OutgoingDecisions),
], debug=True)
