
import os
import logging
import webapp2

from django.utils import simplejson as json

from MasterHandler import MasterHandler, AjaxError
from users.UserDataModels import UserProfile, Psinque, UserEmail
from users.UserManagement import getPublicGroup, getDisplayNameFromPsinque
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
            notifications = Psinque.all().filter("userTo =", self.userProfile).filter("status =", "pending")

            template_values = {
                'notifications': notifications,
                'notificationCount': notifications.count()
            }

            MasterHandler.sendTopTemplate(self, activeEntry = "Outgoing")
            MasterHandler.sendContent(self, 'templates/notifications_view.html', template_values)
            MasterHandler.sendBottomTemplate(self)

app = webapp2.WSGIApplication([
    (r'/outgoing/(\w+)', OutgoingHandler),
], debug=True)
