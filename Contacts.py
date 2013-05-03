# -*- coding: utf-8 -*-
import os
import logging
import webapp2

from google.appengine.api import users

from django.utils import simplejson as json

from MasterHandler import MasterHandler

from users.UserDataModels import UserProfile, UserSettings, availableLanguages, Relationship

class ViewContacts(MasterHandler):
  
  def get(self):
    
    user = users.get_current_user()
    query = UserProfile.all()
    userProfile = query.filter("user =", user).get()
    
    # If the user is not logged in, redirect to main page
    if user == None:
      self.redirect("/")
      return

    userContacts = userProfile.outgoing
          
    template_values = {
      'header': 'Your Contacts:',
      'userContacts': userContacts,
      'howManyContacts': userContacts.count(),
    }

    MasterHandler.sendTopTemplate(self, activeEntry = "Contacts")
    MasterHandler.sendContent(self, 'templates/contacts_viewContacts.html', template_values)
    MasterHandler.sendBottomTemplate(self)

class SearchContacts(MasterHandler):

  def get(self):
    self.redirect("/")
    return

  def post(self):
    
    user = users.get_current_user()
    query = UserProfile.all()

    # Filter the data based on the supplied search criteria
    if self.request.get('firstname'):
      query.filter("firstname =", self.request.get('firstname'))
    if self.request.get('lastname'):
      query.filter("lastname =", self.request.get('lastname'))

    # If user finds himself, or a person which can already be found in his
    # contacts, such an entry should be properly marked in the search results
    contactList = list()

    for profile in query:
      
      if profile.user == user:
        continue
      userFrom = UserProfile.all().filter("user =", user).get()
      userTo = UserProfile.all().filter("user =", profile.user).get()
     
      if Psinque.all().filter('userFrom =', userFrom).filter('userTo =', userTo).get():
        continue
      contactList.append(profile)

    template_values = {
      'header': 'Search Results:',
      'searchResults': contactList,
      'howManyResults': len(contactList),
    }

    MasterHandler.sendTopTemplate(self, activeEntry = "Contacts")
    MasterHandler.sendContent(self, 'templates/contacts_searchContacts.html', template_values)
    MasterHandler.sendBottomTemplate(self)

class AddContact(webapp2.RequestHandler):

  def get(self):

    # Prepare the Datastore row values
    userId = int(self.request.get('id'))
    user = users.get_current_user()
    fromUser = UserProfile.all().filter("user =", user).get()
    toUser = UserProfile.get_by_id(userId)
    status = 'pending'
    
    # Check if a psinque has not already been created
    query = Psinque.all()
    existingPsinque = query.filter('fromUser =', fromUser).filter('toUser =', toUser).get()

    # Create a new psinque unless:
    #  - user tries to add himself as a contact
    #  - a psinque between both users does not already exist
    #  10.08.2012: With slideUp implemented, this code could be removed. Check with Stasiu.
    if (fromUser.key().id() != toUser.key().id()) and (not existingPsinque):
      newPsinque = Psinque()
      newPsinque.fromUser = fromUser
      newPsinque.toUser = toUser
      newPsinque.status = status
      newPsinque.put()
      self.response.out.write(json.dumps({"status": "ok", "userId": userId}))


app = webapp2.WSGIApplication([
  ('/contacts', ViewContacts),
  ('/searchcontacts', SearchContacts),
  ('/addcontact', AddContact),
], debug=True)
