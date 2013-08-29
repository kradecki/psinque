
import webapp2

from google.appengine.ext import db

from MasterHandler import MasterHandler

from DataModels import UserProfile, UserSettings, Permit, Group
from DataModels import UserAddress, UserEmail, UserIM, UserPhoneNumber, UserWebpage
from DataModels import Psinque, Contact, IndividualPermit, CardDAVLogin

@db.transactional
def _deleteprofile(userProfileKey):

    userProfile = UserProfile.get(userProfileKey)    
    
    for e in CardDAVLogin.all().ancestor(userProfile):
        e.delete()
    for e in IndividualPermit.all().ancestor(userProfile):
        e.delete()
    for e in Permit.all().ancestor(userProfile):
        e.delete()
    for e in Psinque.all().ancestor(userProfile):
        e.delete()
    for e in Contact.all().ancestor(userProfile):
        e.delete()
    for e in Group.all().ancestor(userProfile):
        e.delete()
    for e in UserAddress.all().ancestor(userProfile):
        e.delete()
    for e in UserEmail.all().ancestor(userProfile):
        e.delete()
    for e in UserIM.all().ancestor(userProfile):
        e.delete()
    for e in UserPhoneNumber.all().ancestor(userProfile):
        e.delete()
    for e in UserWebpage.all().ancestor(userProfile):
        e.delete()
    
    userProfile.userSettings.delete()
    userProfile.delete()


#-----------------------------------------------------------------------------
# Request handler

class AdminHandler(MasterHandler):

    #****************************
    # Views
    # 
    
    def userprofile(self):
    
        self.sendContent('templates/Admin_UserProfile.html',
                            activeEntry = "",
                            templateVariables = {
            'userProfiles': UserProfile.all(),
        })
        
        
    def deleteprofile(self):
          
        _deleteprofile(self.getRequiredParameter("key"))
        self.sendJsonOK()


#-----------------------------------------------------------------------------

app = webapp2.WSGIApplication([
    (r'/admin/(\w+)', AdminHandler),
], debug=True)
