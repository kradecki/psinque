
import webapp2

from MasterHandler import MasterHandler

from DataModels import UserProfile
from DataManipulation import deleteProfile

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
          
        deleteProfile(self.getRequiredParameter("key"))
        self.sendJsonOK()


#-----------------------------------------------------------------------------

app = webapp2.WSGIApplication([
    (r'/admin/(\w+)', AdminHandler),
], debug=True)
