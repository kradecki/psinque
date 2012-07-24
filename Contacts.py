# -*- coding: utf-8 -*-
import os
import logging

from google.appengine.ext import webapp
from google.appengine.api import users
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.ext.webapp import template

from django.utils import simplejson

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
    MasterHandler.sendContent(self, 'templates/viewContacts.html', template_values)
    MasterHandler.sendBottomTemplate(self)

class SearchContacts(MasterHandler):

  def post(self):

    searchProfile = UserProfile.all()

    # Filter the data based on the supplied search criteria
    if self.request.get('firstname'):
      searchProfile.filter("firstname =", self.request.get('firstname'))
    if self.request.get('lastname'):
      searchProfile.filter("lastname =", self.request.get('lastname'))

    template_values = {
      'header': 'Search Results:',
      'searchResults': searchProfile,
      'howManyResults': searchProfile.count(),
    }

    MasterHandler.sendTopTemplate(self, activeEntry = "Contacts")
    MasterHandler.sendContent(self, 'templates/searchResults.html', template_values)
    MasterHandler.sendBottomTemplate(self)

application = webapp.WSGIApplication([
  ('/contacts', ViewContacts),
  ('/searchcontacts', SearchContacts),
], debug=True)

def main():
  run_wsgi_app(application)

if __name__ == '__main__':
  main()
