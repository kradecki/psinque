# -*- coding: utf-8 -*-
import logging
import webapp2

from google.appengine.api import users

from MasterHandler import MasterHandler
from users.UserDataModels import UserProfile, Relationship

class ViewGroups(MasterHandler):
  
  def get(self):

    MasterHandler.safeGuard(self)
    
    userProfile = UserProfile.all().filter("user =", users.get_current_user()).get()
    userGroups = userProfile.groups
    
    MasterHandler.sendTopTemplate(self, activeEntry = "Groups")
    MasterHandler.sendContent(self, 'templates/groups_viewGroups.html', {
      'groups': userGroups,
    })
    MasterHandler.sendBottomTemplate(self)

#class AddGroup(webapp2.RequestHandler):

  #def get(self):

    ## Prepare the Datastore row values
    #userId = int(self.request.get('id'))
    #user = users.get_current_user()
    #userFrom = UserProfile.all().filter("user =", user).get()
    #userTo = UserProfile.get_by_id(userId)
    #status = 'pending'
    
    ## Check if a relationship has not already been created
    #query = Relationship.all()
    #existingRelationship = query.filter('userFrom =', userFrom).filter('userTo =', userTo).get()

    ## Create a new relationship unless:
    ##  - user tries to add himself as a contact
    ##  - a relationship between both users does not already exist
    ##  10.08.2012: With slideUp implemented, this code could be removed. Check with Stasiu.
    #if (userFrom.key().id() != userTo.key().id()) and (not existingRelationship):
      #newRelationship = Relationship()
      #newRelationship.userFrom = userFrom
      #newRelationship.userTo = userTo
      #newRelationship.status = status
      #newRelationship.put()
      #self.response.out.write(json.dumps({"status": "ok", "userId": userId}))

app = webapp2.WSGIApplication([
  ('/groups', ViewGroups),
], debug=True)
