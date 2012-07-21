# -*- coding: utf-8 -*-
import os
import logging

from google.appengine.ext import webapp
from google.appengine.api import users
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.ext.webapp import template

from MasterHandler import MasterHandler

from UserDataModels import UserProfile, UserSettings, availableLanguages, Relationship

class ViewContacts(MasterHandler):
  
  def get(self):
    user = users.get_current_user()
    query = UserProfile.all()
    userProfile = query.filter("user =", user).get()
    template_values = {
      'message': 'You have currently no contacts',
    }
    for relationship in userProfile.outgoingRelationships:
      logging.info(relationship)
      template_values = {
        'message': 'Your contacts',
      }

    MasterHandler.sendTopTemplate(self, activeEntry = "Contacts")
    MasterHandler.sendContent(self, 'templates/viewContacts.html', template_values)
    MasterHandler.sendBottomTemplate(self)

  def post(self):
    self.redirect('/searchcontacts')  # redirects to SearchContacts

class SearchContacts(MasterHandler):

  def get(self):
    user = users.get_current_user()
    query = UserProfile.all()
    userProfile = query.filter("user =", user).get()
    template_values = {
      'message': 'Find your contacts',
    }
    MasterHandler.sendTopTemplate(self, activeEntry = "Contacts")
    MasterHandler.sendContent(self, 'templates/searchContacts.html', template_values)
    MasterHandler.sendBottomTemplate(self)

  def post(self):
    user = users.get_current_user()
    query = UserProfile.all()
    userProfile = query.filter("user =", user).get()
    contactFirstname = self.request.get('firstname')
    contactLastname = self.request.get('lastname')
    logging.info(query)
    
    contactProfile = query.filter("lastname =", contactLastname)

    template_values = {
      'firstname': contactProfile, # Nie zwraca mi tutaj
      'lastname':  contactLastname,
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
