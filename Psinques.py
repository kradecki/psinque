# -*- coding: utf-8 -*-

import os
import logging
import webapp2

from google.appengine.ext.db import KindError
from google.appengine.api import users, datastore_errors

from django.utils import simplejson as json

from MasterHandler import MasterHandler, AjaxError
from DataModels import Persona
import Notifications

from DataModels import Psinque, Group, Contact, UserEmail, UserProfile
from DataManipulation import contactExists

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
                contact.friendsContact.put()
            contact.delete()
        else:
            contact.put()


    def _clearOutgoing(self, contact):
        contact.outgoing = None
        if contact.incoming is None:
            if not contact.friendsContact is None:
                contact.friendsContact.friendsContact = None
                contact.friendsContact.put()
            contact.delete()
        else:
            contact.put()


    def _downgradePsinqueToPublic(self, psinque):
      
        psinque.parent().status = "public"
        psinque.parent().put()
        
        psinque.private = False
        psinque.persona = psinque.fromUser.publicPersona
        psinque.put()


    def _removeIncoming(self, contact):
        '''
        Removes the incoming Psinque from a Contact. If the Contact
        is empty, it is removed. This Psinque is also removed from
        the friend's Contact. The Psinque is removed as well.
        '''
        if not contact.friendsContact is None:  # in case we use a public psinque, there might be no Contact on the other side
            self._clearOutgoing(contact.friendsContact)
        self._clearIncoming(contact)


    def _removeOutgoing(self, contact):
        '''
        Removes the outgoing Psinque from a Contact. If the Contact
        is empty, it is removed. The Psinque is then downgraded to
        a public psinque, so it's not removed from the friend's
        Contact.
        '''
        if not contact.friendsContact is None:
            self._clearIncoming(contact.friendsContact)
        self._clearOutgoing(contact)


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
        if contact.persona.public:
            contact.persona = self.userProfile.defaultPersona

        contact.status = "pending"
        contact.put()
        
        newPsinque = Psinque(parent = contact,
                             fromUser = friendsProfile,
                             private = True,
                             persona = friendsProfile.defaultPersona,
                             status = "pending")
        newPsinque.put()
        Notifications.notifyPendingPsinque(newPsinque)
    
    
    def _addPublicPsinque(self, friendsProfile):
        
        contact = contactExists(self.userProfile, friendsProfile)
        if contact is None:
            contactExisted = False
            contact = Contact(parent = self.userProfile,
                              friend = friendsProfile,
                              group = self.userProfile.defaultGroup,
                              persona = self.userProfile.publicPersona)
            contact.put()
        
        friendsContact = Contact.all().\
                                 ancestor(friendsProfile).\
                                 filter("friend =", self.userProfile).\
                                 get()
        if not friendsContact is None:
            persona = friendsContact.persona
            if not persona.public:
                contact.status = "private"
        else:
            persona = friendsProfile.publicPersona
        
        newPsinque = Psinque(parent = contact,
                             fromUser = friendsProfile,
                             private = False,
                             persona = persona,
                             status = "established")
        newPsinque.put()
        
        if not friendsContact is None:
            if friendsContact.incoming:
                contact.outgoing = friendsContact.incoming
            friendsContact.outgoing = newPsinque
            friendsContact.put()
        
        contact.incoming = newPsinque
        contact.put()
        
        return [contactExisted, contact, newPsinque]
    
    
    def _sendNewContact(self, contact):

        personaList = { persona.key(): persona.name for persona in self.userProfile.personas.fetch(100) }         
        groupList = { group.key(): group.name for group in self.userProfile.groups.fetch(100) }
                
        self.sendContent('templates/Psinques_Contact.html',
                        templateVariables = {
            'contact': contact,
            'groups': groupList,
            'personas': personaList,
        })

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
            pendingList = [{'name': x.parent().persona.displayName,
                            'key': str(x.key())} for x in pendingPsinques]

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

            personaList = { persona.key(): persona.name for persona in self.userProfile.personas.fetch(100) }         
            groupList = { group.key(): group.name for group in self.userProfile.groups.fetch(100) }
                    
            self.sendContent('templates/Psinques.html',
                            activeEntry = "Psinques",
                            templateVariables = {
                'offset': offset,
                'isThereMore': (offset + len(contacts) < count),
                'count': count,
                'nextCursor': contactQuery.cursor(),
                'contacts': contacts,
                'pendings': pendingList,
                'groups': groupList,
                'personas': personaList,
            })

    
    #****************************
    # AJAX methods
    # 
    
    def searchemail(self):

        # Search for the owner of the email address
        email = self.request.get('email')
        email = email.lower()
        
        userEmail = UserEmail.all(keys_only = True). \
                              filter("itemValue =", email). \
                              get()
        if not userEmail:
          
            self.sendJsonOK({ "found": False })
        
        else:
          
            # Check if it's not my own email address
            userProfile = UserProfile.get(userEmail.parent())
            if userProfile.key() == self.userProfile.key():
                raise AjaxError("It is your own email address.")
              
            # Check if there already is a Psinque from that user
            psinque = self._getPsinqueFrom(userProfile)
            if not psinque is None:
                raise AjaxError("You already have a psinque with this email address.")

            # Check if the account is active
            if not userProfile.active:
                self.sendJsonOK({ "found": False })  # act like this person is not registered

            self.sendJsonOK({
                "found": True,
                "key": str(userProfile.key()),
                "displayName": userProfile.displayName,
                "publicEnabled": userProfile.publicEnabled,
            })


    def addpublic(self):
                
        friendsProfile = UserProfile.get(self.getRequiredParameter("key"))
        
        psinque = self._getPsinqueFrom(friendsProfile)
        if not psinque is None:
            raise AjaxError("You already have this psinque")
        
        contact = self._addPublicPsinque(friendsProfile)
        if not contact[0]:
            self._sendNewContact(contact[1])
        else:
            raise AjaxError("Incoming psinque already exists.")


    def requestprivate(self):
        
        contact = self._getContact()
        
        existingPsinque = Psinque.all(keys_only = True). \
                                  ancestor(contact). \
                                  filter("private =", True). \
                                  get()
        if not existingPsinque is None:
            raise AjaxError("Request has already been sent.")
        
        self._addRequestToUpgrade(contact, contact.friend)
        self.sendJsonOK()
    
    
    def addincoming(self):
      
        contact = self._getContact()
        if contact.incoming:
            raise AjaxError("Incoming psinque already exists.")
        
        friendsProfle = contact.friendsContact.parent()
        newPsinque = Psinque(parent = contact,
                             fromUser = friendsProfle,
                             private = True,
                             persona = friendsProfle.defaultPersona,
                             status = "established")
        newPsinque.put()
        
        contact.incoming = newPsinque
        contact.put()
        
        contact.friendsContact.outgoing = newPsinque
        contact.friendsContact.put()
        
        self._sendNewContact(contact)


    def removecontact(self):
        
        contact = self._getContact()
        if contact.incoming:
            contact.incoming.delete()

        if not contact.friendsContact is None:
            contact.friendsContact.outgoing = None
            contact.friendsContact.friendsContact = None
            contact.friendsContact.put()

        contact.delete()

        self.sendJsonOK()
                       

    def changepersona(self):

        try:
            contact = Contact.get(self.getRequiredParameter('contact'))
        except datastore_errors.BadKeyError:
            raise AjaxError("Contact does not exist")

        try:
            persona  = Persona.get(self.getRequiredParameter('persona'))
        except datastore_errors.BadKeyError:
            raise AjaxError("Persona does not exist")
        
        if contact.persona == persona:
          
            self.sendJsonOK()
            return
          
        contact.persona = persona
        contact.put()
        
        if persona.public:
          
            if contact.outgoing:
                contact.outgoing.private = False
                contact.outgoing.put()
                Notifications.notifyDowngradedPsinque(contact.outgoing)
            
            if contact.friendsContact:
                contact.friendsContact.status = "public"
                contact.friendsContact.put()
                    
        if contact.outgoing:
            contact.outgoing.persona = persona
            contact.outgoing.put()
            
        self.sendJsonOK()


    def changegroup(self):
        
        try:
            contact = Contact.get(self.getRequiredParameter('contact'))
        except datastore_errors.BadKeyError:
            raise AjaxError("Contact does not exist")

        #oldGroup = contact.group

        try:
            persona  = Group.get(self.getRequiredParameter('persona'))
        except datastore_errors.BadKeyError:
            raise AjaxError("Group does not exist")
        
        # First we check if this psinque is not already asigned to that group
        contact.group = group
        contact.put()
        
        #oldGroupSize = Contact.all(keys_only = True). \
                               #filter("group =", oldGroup). \
                               #count(1)
        #if oldGroupSize == 0:
            #olfGroup.delete()
            
        self.sendJsonOK()

    
    def acceptrequest(self):
        
        try:
            psinque = self._getPsinqueByKey()
        except AjaxError:
            self.displayMessage('templates/Message_PsinqueNotFound.html')
            return
        
        contactIn = self._getContactForIncoming(psinque)
        contactOut = self._getContactForOutgoing(psinque)

        if contactOut is None:
            contactOut = Contact(parent = self.userProfile,
                                 friend = contactIn.parent(),
                                 friendsContact = contactIn,
                                 group = self.userProfile.defaultGroup,
                                 persona = self.userProfile.defaultPersona)
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
        contactIn.status = "private"
        contactIn.persona = contactIn.parent().defaultPersona
        contactIn.put()
        
        contactOut.outgoing = psinque
        contactOut.status = "private"
        contactOut.persona = contactOut.parent().defaultPersona
        contactOut.put()
        
        psinque.status = "established"
        psinque.persona = psinque.fromUser.defaultPersona
        psinque.put()
        
        Notifications.notifyAcceptedRequest(psinque)
        
        if self.request.get("email") == "true":
            self.displayMessage('templates/Message_Accepted.html',
                            templateVariables = {
                    'friendsName': contactOut.displayName,
                })
        else:
            self._sendNewContact(contactOut)
    
    
    def rejectrequest(self):
        
        psinque = self._getPsinqueByKey()       
        psinque.delete()

        Notifications.notifyRejectedRequest(psinque)
        
        if self.request.get("email") == "true":
            self.displayMessage('templates/Message_Rejected.html',
                            templateVariables = {
                    'friendsName': psinque.displayName,
                })
        else:
            self.sendJsonOK()


    def banrequest(self):
        
        raise AjaxError("Unimplemented")
      
      
    def addgroup(self):
        
        group = Group(parent = self.userProfile,
                      name = self.getRequiredParameter("name"))
        group.put()
        
        self.sendJsonOK({
            "key": str(group.key()),
        })
        
#-----------------------------------------------------------------------------

app = webapp2.WSGIApplication([
    (r'/psinques/(\w+)', PsinquesHandler),
    #(r'/decisions/(\w+)', OutgoingDecisions),
], debug=True)
