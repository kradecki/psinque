
import os
import logging
import webapp2

from google.appengine.api import users

from django.utils import simplejson as json

from MasterHandler import MasterHandler
from users.UserDataModels import UserProfile, Psinque

class Outgoing(MasterHandler):
  
  def get(self):
    
    currentUserProfile = UserProfile.all().filter("user =", users.get_current_user()).fetch(1)[0]
    notifications = Psinque.all().filter("userTo =", currentUserProfile).filter("status =", "pending")

    template_values = {
      'notifications': notifications,
      'notificationCount': notifications.count()
    }

    MasterHandler.sendTopTemplate(self, activeEntry = "Outgoing")
    MasterHandler.sendContent(self, 'templates/notifications_view.html', template_values)
    MasterHandler.sendBottomTemplate(self)

class ChangeRelationship(webapp2.RequestHandler):

  def get(self):

    currentUserProfile = UserProfile.all().filter("user =", users.get_current_user()).fetch(1)[0]
    psinque = Psinque.get_by_id(int(self.request.get('id')))
    if psinque.userTo.user == users.get_current_user():
      # We still want to filter only the current user to avoid situation when a user changes
      # relationships of other users by sending a fake GET query
      psinque.status = self.request.get('to')
      psinque.put()
      self.response.out.write(json.dumps({"status": "ok"}))

app = webapp2.WSGIApplication([
  ('/outgoing', Outgoing),
  ('/changerelationship', ChangeRelationship),
], debug=True)
