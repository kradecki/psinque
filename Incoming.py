
import os
import logging
import webapp2

from django.utils import simplejson as json

from MasterHandler import MasterHandler, AjaxError
from users.UserDataModels import UserProfile, Psinque, UserEmail
from users.UserManagement import getPublicGroup, getIncomingDisplayNameFromPsinque
from users.Email import notifyPendingPsinque

#-----------------------------------------------------------------------------

class IncomingHandler(MasterHandler):

    def get(self, actionName):
        
        if MasterHandler.safeGuard(self):
            
            actionFunction = getattr(self, actionName)
            
            try:
                actionFunction()
            except AjaxError as e:
                self.sendJsonError(e.value)

    def view(self):
        
        if MasterHandler.getUserProfile(self):
            
            offset = self.request.get('offset')
            if not offset:
                offset = 0
            else:
                offset = int(offset)
            currentCursor = self.request.get('cursor')
            
            psinqueQuery = Psinque.all(keys_only = True).ancestor(self.userProfile).order("establishingTime")
            count = psinqueQuery.count(1000)
            contacts = []
            if currentCursor:
                psinqueQuery.with_cursor(currentCursor)  # start from the previous position
            for psinqueKey in psinqueQuery.run(limit=10):
                psinque = Psinque.get(psinqueKey)
                contacts.append({'nr': offset + len(contacts) + 1,
                                 'name': getIncomingDisplayNameFromPsinque(psinque),
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
                self.redirect('/incoming')
                
            elif incomingType == "private":
                newPsinque = Psinque(parent = self.userProfile, toUser = self.userProfile,
                                    fromUser = fromUser,
                                    status = "pending")
                newPsinque.put()
                notifyPendingPsinque(newPsinque)
                self.response.out.write(json.dumps({"status": 0}))
                
            else:
                self.response.out.write(json.dumps({"status": 1}))


    def removepsinque(self):
        
        psinque = Psinque.get(self.checkGetParameter('key'))
        if not psinque is None:
            psinque.delete()
        self.redirect("/incoming")
        
#-----------------------------------------------------------------------------

app = webapp2.WSGIApplication([
    (r'/incoming/(\w+)', IncomingHandler),
], debug=True)
