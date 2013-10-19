
import webapp2 
import jinja2
import os

from google.appengine.api import users

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

directOpenIDNames = ["Google+", "Yahoo!", "Yahoo! Japan"]

#-----------------------------------------------------------------------------

class OpenIdLoginHandler(webapp2.RequestHandler):
  
    def get(self):
      
        continue_url = self.request.GET.get('continue')

        template = jinja_environment.get_template('templates/Landing.html')
        self.response.out.write(template.render({
            'loginurls': zip([users.create_login_url(dest_url = continue_url,
                                                     federated_identity = uri)
                             for uri in directOpenIDProviders],
                             directOpenIDIconNames,
                             directOpenIDNames)
        }))
    
app = webapp2.WSGIApplication([
    ('/_ah/login_required', OpenIdLoginHandler),
], debug=True)
