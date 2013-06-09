# -*- coding: utf-8 -*-

import os
import logging
import webapp2

from google.appengine.ext.db import KindError

from django.utils import simplejson as json

from MasterHandler import MasterHandler, AjaxError
from Permits import Permit
import Notifications

from DataModels import Psinque, Group, Contact, UserEmail, UserProfile

#-----------------------------------------------------------------------------

class PsinquesHandler(MasterHandler):

    #****************************
    # Private methods
    # 

    def _getContact(self):

        # Find contact on this end
        contact = Contact.get(self.getRequiredParameter('key'))
        if contact is None:
            raise AjaxError("Contact not found")
            
        if contact.parent().key() != self.userProfile.key():
            raise AjaxError("You cannot modify contacts that do not belong to you")
        
        return contact
    
    
    def _getContactForOutgoing(self, psinque):
        '''
        Finds and returns a Contact that has the "psinque" in the 
        "outgoing" field. This Contact will belong to an unknown
        user, so we cannot use ancestor queries.
        '''
        return psinque.parent().friendsContact
        #return Contact.all(). \
                       #ancestor(psinque.fromUser). \
                       #filter("outgoing =", psinque). \
                       #get()

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
            if not contact.friendsContact is None:
                contact.friendsContact.friendsContact = None
            contact.delete()


    def _clearOutgoing(self, contact):
        contact.outgoing = None
        if contact.incoming is None:
            if not contact.friendsContact is None:
                contact.friendsContact.friendsContact = None
                contact.friendsContact.put()
            contact.delete()

    def _downgradePsinqueToPublic(self, psinque):
        psinque.private = False
        psinque.permit = psinque.fromUser.publicPermit
        psinque.put()


    def _removeIncoming(self, contact):
        '''
        Removes the incoming Psinque from a Contact. If the Contact
        is empty, it is removed. This Psinque is also removed from
        the friend's Contact. The Psinque is removed as well.
        '''
        if (not contact.incoming is None) and contact.incoming.private:
            Notifications.notifyStoppedUsingPrivateData(contact.incoming)
        if not contact.friendsContact is None:  # in case we use a public psinque, there might be no Contact on the other side
            self._clearOutgoing(contact.friendsContact)
        self._clearIncoming(contact)

        for psinque in Psinque.all().ancestor(contact):
            psinque.delete()


    def _removeOutgoing(self, contact):
        '''
        Removes the outgoing Psinque from a Contact. If the Contact
        is empty, it is removed. The Psinque is then downgraded to
        a public psinque, so it's not removed from the friend's
        Contact.
        '''
        psinque = contact.outgoing
        if not psinque is None:
            Notifications.notifyDowngradedPsinque(psinque)
            self._clearOutgoing(contact)
            self._downgradePsinqueToPublic(psinque)


    def _getPsinqueByKey(self):
        
        psinqueKey = self.getRequiredParameter('key')
        psinque = Psinque.get(psinqueKey)
        if psinque is None:
            raise AjaxError("Psinque not found.")
        return psinque

    
    def _getPsinqueFrom(self, userProfile):
        return Psinque.all(keys_only = True). \
                       ancestor(self.userProfile). \
                       filter("fromUser =", userProfile). \
                       get()
    
    
    def _addRequestToUpgrade(self, contact, friendsProfile):

        if contact.incoming.private:
            raise AjaxError("You already have access to private data")
        
        # We need to share our own private data first
        if contact.permit.public:
            contact.permit = self.userProfile.defaultPermit
            contact.put()
        
        newPsinque = Psinque(parent = contact,
                             private = True,
                             fromUser = friendsProfile,
                             status = "pending")
        newPsinque.put()
        Notifications.notifyPendingPsinque(newPsinque)
    
    
    def _addPublicPsinque(self, friendsProfile):
        
        contact = Contact.all(). \
                          ancestor(self.userProfile). \
                          filter("friend =", friendsProfile). \
                          get()
        if contact is None:
            contact = Contact(parent = self.userProfile,
                              friend = friendsProfile,
                              group = self.userProfile.defaultGroup,
                              permit = self.userProfile.publicPermit)
            contact.put()
        
        newPsinque = Psinque(parent = contact,
                             fromUser = friendsProfile,
                             private = False,
                             permit = friendsProfile.defaultPermit,
                             status = "established")
        newPsinque.put()
        
        contact.incoming = newPsinque
        contact.put()
        
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
                pendingList.append({'name': pending.parent().permit.displayName,
                                    'key': str(pending.key())})

            # List of contacts
            contactQuery = Contact.all(). \
                                    ancestor(self.userProfile). \
                                    order("creationTime")
                                
            count = contactQuery.count(1000)
            if currentCursor:
                contactQuery.with_cursor(currentCursor)  # start from the previous position
            contacts = contactQuery.fetch(limit = 10)
            
            if len(contacts) == 10:
                isThereMore = (offset + 10 < count)
            else:
                isThereMore = False
                    
            self.sendContent('templates/psinques_view.html',
                            activeEntry = "Psinques",
                            templateVariables = {
                'offset': offset,
                'isThereMore': (offset + len(contacts) < count),
                'count': count,
                'nextCursor': contactQuery.cursor(),
                'contacts': contacts,
                'pendings': pendingList,
                'groups': Group.all().ancestor(self.userProfile),
                'permits': Permit.all().ancestor(self.userProfile).filter("public =", False),
            })


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

        if userEmail is None:
            raise AjaxError("User not found")
        
        # Check if there already is a Psinque from that user
        userProfile = UserProfile.get(userEmail.parent())
        logging.info(userProfile)
        psinque = self._getPsinqueFrom(userProfile)
        if not psinque is None:
            raise AjaxError("Psinque already exists")
        
        self.sendJsonOK({
            "key": str(userProfile.key()),
            "publicEnabled": userProfile.publicEnabled,
        })


    def requestupgrade(self):
        
        contact = self._getContact()
        
        existingPsinque = Psinque.all(keys_only = True). \
                                  ancestor(contact). \
                                  filter("private =", True). \
                                  get()
        if not existingPsinque is None:
            raise AjaxError("Request has already been sent.")
        
        self._addRequestToUpgrade(contact, contact.friend)
        self.sendJsonOK()
    

    def addpublic(self):
                
        friendsProfile = UserProfile.get(self.getRequiredParameter("key"))

        psinque = self._getPsinqueFrom(friendsProfile)
        logging.info(psinque)
        if not psinque is None:
            raise AjaxError("You already have this psinque")
        
        self._addPublicPsinque(friendsProfile)
        
        self.redirect("/psinques/view")


    def addprivate(self):
        
        try:
            friendsProfile = UserProfile.get(self.getRequiredParameter("key"))
        except KindError:
            friendsProfile = Contact.get(self.getRequiredParameter("key")).friend
        
        psinque = self._getPsinqueFrom(friendsProfile)
        if not psinque is None:
            if psinque.private:
                raise AjaxError("You already have this psinque")
            else:
                self._addRequestToUpgrade(psinque.parent(), friendsProfile)
        else:
            newPsinque = self._addPublicPsinque(friendsProfile)
            self._addRequestToUpgrade(newPsinque.parent(), friendsProfile)
        
        self.sendJsonOK()


    def removeincoming(self):
        
        self._removeIncoming(self._getContact())

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
        if contact is None:
            raise AjaxError("Contact does not exist")

        permit  = Permit.get(self.getRequiredParameter('permit'))
        if permit is None:
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

        if contactOut is None:
            contactOut = Contact(parent = self.userProfile,
                                 friend = contactIn.parent(),
                                 friendsContact = contactIn,
                                 group = self.userProfile.defaultGroup,
                                 permit = self.userProfile.defaultPermit)
            contactOut.put()
            contactIn.friendsContact = contactOut
                                         
        if not contactOut.outgoing is None:
            raise AjaxError("There already is a psinque from this user")
        
        existingPsinque = contactIn.incoming
        if not existingPsinque is None:
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
