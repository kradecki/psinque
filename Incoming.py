
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
        else:
            offset = int(offset)
        currentCursor = self.request.get('cursor')
        
        psinqueQuery = Psinque.all(keys_only = True).ancestor(userProfile).order("establishingTime")
        count = psinqueQuery.count(1000)
        contacts = []
        if currentCursor:
            psinqueQuery.with_cursor(currentCursor)  # start from the previous position
        for psinqueKey in psinqueQuery.run(limit=10):
            psinque = Psinque.get(psinqueKey)
            contacts.append({'nr': offset + len(contacts) + 1,
                             'name': getDisplayNameFromPsinque(psinque),
                             'date': psinque.establishingTime,
                             'status': psinque.status,
                             'key': psinque.key(),
                           })
        template_values = {
            'offset': offset,
            'isThereMore': (offset + len(contacts) < count),
            'count': count,
            'nextCursor': psinqueQuery.cursor(),
            'contacts': contacts,
        }
                
        MasterHandler.sendTopTemplate(self, activeEntry = "Incoming")
        MasterHandler.sendContent(self, 'templates/incoming_view.html', template_values)
        MasterHandler.sendBottomTemplate(self)

#-----------------------------------------------------------------------------

class IncomingAJAX(MasterHandler):
    '''
    Hangles AJAX requests regarding incoming psinques.
    '''

    def get(self, methodName):
        
        MasterHandler.safeGuard(self)
        ajaxMethod = getattr(self, methodName)
        ajaxMethod()


    def searchemail(self):

        email = self.request.get('email')
        userEmail = UserEmail.all(keys_only = True).filter("email =", email).get()
        if userEmail:
            userID = userEmail.parent().id()
            userProfile = UserProfile.all(keys_only = True).filter("user =", self.user).get()
            psinque = Psinque.all(keys_only = True).ancestor(userProfile).filter("fromUser =", userEmail.parent()).get()
            if psinque:
                self.response.out.write(json.dumps({"status": 1})) # psinque already exists
            else:
                self.response.out.write(json.dumps({"status": 0, "fromUser": userID}))
        else:
            self.response.out.write(json.dumps({"status": -1}))   # user not found


    def addincoming(self):
        
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
            self.response.out.write(json.dumps({"status": 0}))
            
        else:
            self.response.out.write(json.dumps({"status": 1}))


    def removepsinque(self):
        
        psinque = Psinque.get(self.request.get('key'))
        psinque.delete()
        self.redirect("/incoming")
        
#-----------------------------------------------------------------------------

app = webapp2.WSGIApplication([
    (r'/incoming', Incoming),
    (r'/incoming/(\w+)', IncomingAJAX),
], debug=True)
