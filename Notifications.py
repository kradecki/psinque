
import os
import logging

from google.appengine.ext import webapp
from google.appengine.api import users
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.ext.webapp import template

from django.utils import simplejson as json

from MasterHandler import MasterHandler
from UserDataModels import UserProfile, Relationship

class Notifications(MasterHandler):
  
  def get(self):
    
    currentUserProfile = UserProfile.all().filter("user =", users.get_current_user()).fetch(1)[0]
    notifications = Relationship.all().filter("userTo =", currentUserProfile).filter("status =", "pending")

    template_values = {
      'notifications': notifications,
      'notificationCount': notifications.count()
    }

    MasterHandler.sendTopTemplate(self, activeEntry = "Notifications")
    MasterHandler.sendContent(self, 'templates/notifications_view.html', template_values)
    MasterHandler.sendBottomTemplate(self)

class ChangeRelationship(webapp.RequestHandler):

  def get(self):

    currentUserProfile = UserProfile.all().filter("user =", users.get_current_user()).fetch(1)[0]
    relationship = Relationship.get_by_id(int(self.request.get('id')))
    if relationship.userTo.user == users.get_current_user():
      # We still want to filter only the current user to avoid situation when a user changes
      # relationships of other users by sending a fake GET query
      relationship.status = self.request.get('to')
      relationship.put()
      self.response.out.write(json.dumps({"status": "ok"}))

application = webapp.WSGIApplication([
  ('/notifications', Notifications),
  ('/changerelationship', ChangeRelationship),
], debug=True)

def main():
  run_wsgi_app(application)

if __name__ == '__main__':
  main()
