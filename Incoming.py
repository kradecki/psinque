
import os
import logging
import webapp2

from google.appengine.api import users

from MasterHandler import MasterHandler
from users.UserDataModels import UserProfile, Psinque
from users.Emails import notifyPendingPsinque

#-----------------------------------------------------------------------------

class Incoming(MasterHandler):
    
    def get(self):
        
        MasterHandler.safeGuard(self)   
        userProfile = UserProfile.all().filter("user =", self.user).get()
        
        contactsQuery = Psinque.all().ancestor(userProfile).order("establishingTime")
        contactsQuery.run(limit=10)
            
        template_values = {
            'contacts': contactsQuery,
        }
                
        MasterHandler.sendTopTemplate(self, activeEntry = "Incoming")
        MasterHandler.sendContent(self, 'templates/incoming_view.html', template_values)
        MasterHandler.sendBottomTemplate(self)

#-----------------------------------------------------------------------------

class SearchEmail(webapp2.RequestHandler):

    def get(self):

        email = self.request.get('email')
        user = UserEmail.all(keys_only = True).filter("email =", email).get()
        if user:
            self.response.out.write(json.dumps({"status": 1, "fromUser": user}))
        else:
            self.response.out.write(json.dumps({"status": 0}))

#-----------------------------------------------------------------------------

class AddIncoming(MasterHandler):
    
    def get(self):
        
        MasterHandler.safeGuard(self)   
        toUser = UserProfile.all().filter("user =", self.user).get()
        fromUser = UserProfile.get(self.request.get('from'))  # get user by key
        
        incomingType = self.request.get('type')
        if incomingType == "public":
            newPsinque = Psinque(parent = toUser, toUser = toUser, 
                                 fromUser = fromUser,
                                 status = "established",
                                 group = getPublicGroup(fromUser))
            newPsinque.put()
            self.response.out.write(json.dumps({"status": 1}))
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
