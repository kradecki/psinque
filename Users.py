
from google.appengine.api import users

class UserLoggedInHandler(webapp2.RequestHandler):

    def safeGuard(self):

    	self.user = users.get_current_user()
	if not self.user:   # no OpenID user logged in
	
	    if not self._checkCookies():

	        self.redirect("/")

