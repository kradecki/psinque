
import webapp2 
import jinja2
import os

from Users import getCurrentUser

jinja_environment = jinja2.Environment(
    loader = jinja2.FileSystemLoader(os.path.dirname(__file__))
)

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
    
application = webapp2.WSGIApplication([
    ('/_ah/login_required', OpenIdLoginHandler),
], debug=True)
