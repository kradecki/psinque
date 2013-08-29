
import os
import webapp2
import jinja2

from google.appengine.ext import db

from MasterHandler import MasterHandler

from DataModels import UserProfile, UserSettings, Permit, Group
from DataModels import UserAddress, UserEmail, UserIM, UserPhoneNumber, UserWebpage
from DataModels import Psinque, Contact, IndividualPermit, CardDAVLogin

@db.transactional
def _deleteprofile(self, userProfileKey):
    
    for e in CardDAVLogin.all().ancestor(userProfileKey):
        e.delete()
    for e in IndividualPermit.all().ancestor(userProfileKey):
        e.delete()
    for e in Permit.all().ancestor(userProfileKey):
        e.delete()
    for e in Psinque.all().ancestor(userProfileKey):
        e.delete()
    for e in Contact.all().ancestor(userProfileKey):
        e.delete()
    for e in Group.all().ancestor(userProfileKey):
        e.delete()
    for e in UserAddress.all().ancestor(userProfileKey):
        e.delete()
    for e in UserEmail.all().ancestor(userProfileKey):
        e.delete()
    for e in UserIM.all().ancestor(userProfileKey):
        e.delete()
    for e in UserPhoneNumber.all().ancestor(userProfileKey):
        e.delete()
    for e in UserWebpage.all().ancestor(userProfileKey):
        e.delete()
    userProfile = UserProfile.get(userProfileKey)    
    userProfile.userSettings.delete()
    userProfile.delete()


#-----------------------------------------------------------------------------
# Request handler

jinja_environment = jinja2.Environment(
    loader = jinja2.FileSystemLoader(os.path.dirname(__file__))
)

class AdminHandler(webapp2.RequestHandler):

    #****************************
    # Views
    # 
    
    def get(self):
     
    
        template = jinja_environment.get_template('templates/Admin_UserProfile.html')
        self.response.out.write(template.render({
            'userProfiles': UserProfile.all(),
        }))
          
        #_deleteprofile(self.getRequiredParameter("key"))


#-----------------------------------------------------------------------------

app = webapp2.WSGIApplication([
    ('/admin/userprofile', AdminHandler),
], debug=True)
