
import os
import logging
import webapp2

from google.appengine.api import users

from MasterHandler import MasterHandler
from users.UserDataModels import UserProfile, Relationship

class Incoming(MasterHandler):
  
  def get(self):
    MasterHandler.safeGuard(self)   
    userProfile = UserProfile.all().filter("user =", MasterHandler.user).get()

    contacts = userProfile.
    template_values = {
      'contacts': contacts,
    }

    MasterHandler.sendTopTemplate(self, activeEntry = "Incoming")
    MasterHandler.sendContent(self, 'templates/incoming_view.html', template_values)
    MasterHandler.sendBottomTemplate(self)

app = webapp2.WSGIApplication([
  ('/incoming', Incoming),
], debug=True)
