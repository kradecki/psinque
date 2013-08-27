
class AdminHandler(MasterHandler):
  
    def userprofile(self):
    
          self.sendContent('templates/Admin_UserProfile.html',
                          templateVariables = {
              'userProfiles': UserProfile.all(),
          })

app = webapp2.WSGIApplication([
    ('/admin/(\w+)', AdminHandler)
], debug=True)
