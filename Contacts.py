# -*- coding: utf-8 -*-
import os
import logging

from google.appengine.ext import webapp
from google.appengine.api import users
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.ext.webapp import template

from django.utils import simplejson as json

from MasterHandler import MasterHandler

from UserDataModels import UserProfile, UserSettings, availableLanguages, Relationship

class ViewContacts(MasterHandler):
  
  def get(self):
    
    user = users.get_current_user()
    query = UserProfile.all()
    userProfile = query.filter("user =", user).get()
    
    # If the user is not logged in, redirect to main page
    if user == None:
      self.redirect("/")
      return

    userContacts = userProfile.outgoingRelationships
          
    template_values = {
      'header': 'Your Contacts:',
      'userContacts': userContacts,
      'howManyContacts': userContacts.count(),
    }

    MasterHandler.sendTopTemplate(self, activeEntry = "Contacts")
    MasterHandler.sendContent(self, 'templates/contacts_viewContacts.html', template_values)
    MasterHandler.sendBottomTemplate(self)

class SearchContacts(MasterHandler):

  def post(self):

    query = UserProfile.all()

    # Filter the data based on the supplied search criteria
    if self.request.get('firstname'):
      query.filter("firstname =", self.request.get('firstname'))
    if self.request.get('lastname'):
      query.filter("lastname =", self.request.get('lastname'))

    template_values = {
      'header': 'Search Results:',
      'searchResults': query,
      'howManyResults': query.count(),
    }

    MasterHandler.sendTopTemplate(self, activeEntry = "Contacts")
    MasterHandler.sendContent(self, 'templates/contacts_searchContacts.html', template_values)
    MasterHandler.sendBottomTemplate(self)

class AddContact(webapp.RequestHandler):

  def get(self):

    # Prepare the Datastore row values
    userId = int(self.request.get('id'))
    user = users.get_current_user()
    user1 = UserProfile.all().filter("user =", user).get()
    user2 = UserProfile.get_by_id(userId)
    status = 'pending'
    
    # Check if a relationship has not already been created
    query = Relationship.all()
    existingRelationship = query.filter('user1 =', user1).filter('user2 =', user2).get()

    # Create a new relationship unless:
    #  - user tries to add himself as a contact
    #  - a relationship between both users does not already exist
    if (user1.key().id() != user2.key().id()) and (not existingRelationship):
      newRelationship = Relationship()
      newRelationship.user1 = user1
      newRelationship.user2 = user2
      newRelationship.status = status
      newRelationship.put()
      self.response.out.write(json.dumps({"status": "ok", "userId": userId}))


application = webapp.WSGIApplication([
  ('/contacts', ViewContacts),
  ('/searchcontacts', SearchContacts),
  ('/addcontact', AddContact),
], debug=True)

def main():
  run_wsgi_app(application)

if __name__ == '__main__':
  main()