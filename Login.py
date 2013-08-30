
import webapp2 
import jinja2
import os

from google.appengine.api import users

from Users import getCurrentUser

#-----------------------------------------------------------------------------

jinja_environment = jinja2.Environment(
    loader = jinja2.FileSystemLoader(os.path.dirname(__file__))
)

#-----------------------------------------------------------------------------

directOpenIDProviders = [
    'https://www.google.com/accounts/o8/id',
    'yahoo.com',
    'yahoo.co.jp',
]

directOpenIDIconNames = ['google', 'yahoo', 'yahoo_japan']

#-----------------------------------------------------------------------------

class OpenIdLoginHandler(webapp2.RequestHandler):
  
    def get(self):
      
        continue_url = self.request.GET.get('continue')

        template = jinja_environment.get_template('templates/Landing.html')
        self.response.out.write(template.render({
            'loginurls': zip([users.create_login_url(dest_url = continue_url,
                                                     federated_identity = uri)
                             for uri in directOpenIDProviders],
                             directOpenIDIconNames)
        }))
    
app = webapp2.WSGIApplication([
    ('/_ah/login_required', OpenIdLoginHandler),
], debug=True)
