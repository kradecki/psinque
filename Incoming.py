
import os
import logging
import webapp2

from django.utils import simplejson as json

from google.appengine.api import users

from MasterHandler import MasterHandler
from users.UserDataModels import UserProfile, Psinque, UserEmail
from users.UserManagement import getPublicGroup, getDisplayNameFromPsinque
from users.Email import notifyPendingPsinque

#-----------------------------------------------------------------------------

class Incoming(MasterHandler):
    
    def get(self):
        
        MasterHandler.safeGuard(self)   
        userProfile = UserProfile.all().filter("user =", self.user).get()
        
        offset = self.request.get('offset')
        if not offset:
            offset = 0
        previousCursor = self.request.get('cursor')
        
        psinqueQuery = Psinque.all(keys_only = True).ancestor(userProfile).order("establishingTime")
        count = psinqueQuery.count(1000)
        contacts = []
        if previousCursor:
            psinqueQuery.cursor(previousCursor)  # start from the previous position
        for psinqueKey in psinqueQuery.run(limit=10):
            psinque = Psinque.get(psinqueKey)
            contacts.append({'nr': offset + len(contacts) + 1,
                             'name': getDisplayNameFromPsinque(psinque),
                             'date': psinque.establishingTime,
                             'status': psinque.status})
            
        template_values = {
            'offset': offset,
            'isThereMore': (offset + len(contacts) < count),
            'count': count,
            'cursor': psinqueQuery.cursor(),
            'previousCursor': previousCursor,
            'contacts': contacts,
        }
                
        MasterHandler.sendTopTemplate(self, activeEntry = "Incoming")
        MasterHandler.sendContent(self, 'templates/incoming_view.html', template_values)
        MasterHandler.sendBottomTemplate(self)

#-----------------------------------------------------------------------------

class SearchEmail(webapp2.RequestHandler):

    def get(self):

        email = self.request.get('email')
        userEmail = UserEmail.all(keys_only = True).filter("email =", email).get()
        if userEmail:
            userID = userEmail.parent().id()
            self.response.out.write(json.dumps({"status": 1, "fromUser": userID}))
        else:
            self.response.out.write(json.dumps({"status": 0}))

#-----------------------------------------------------------------------------

class AddIncoming(MasterHandler):
    
    def get(self):
        
        MasterHandler.safeGuard(self)   
        toUser = UserProfile.all().filter("user =", self.user).get()
        fromUser = UserProfile.get_by_id(int(self.request.get('from')))  # get user by key
        
        incomingType = self.request.get('type')
        if incomingType == "public":
            newPsinque = Psinque(parent = toUser, toUser = toUser, 
                                 fromUser = fromUser,
                                 status = "established",
                                 group = getPublicGroup(fromUser))
            newPsinque.put()
            self.redirect('/incoming')
            
        elif incomingType == "private":
            newPsinque = Psinque(parent = toUser, toUser = toUser, 
                                 fromUser = fromUser,
                                 status = "pending")
            newPsinque.put()
            notifyPendingPsinque(newPsinque)
            self.response.out.write(json.dumps({"status": 1}))
            
        else:
            self.response.out.write(json.dumps({"status": 0}))
        
#-----------------------------------------------------------------------------

app = webapp2.WSGIApplication([
    ('/incoming', Incoming),
    ('/searchemail', SearchEmail),
    ('/addincoming', AddIncoming),
], debug=True)
