# -*- coding: utf-8 -*-

import os
import webapp2
import jinja2

from google.appengine.api import users


jinja_environment = jinja2.Environment(
    loader = jinja2.FileSystemLoader(os.path.dirname(__file__)))


class StartPage(webapp2.RequestHandler):
  
  def get(self):
    
    user = users.get_current_user()
    if not user:    # user not logged in
        self.redirect("/static/landing")
    else:
        self.redirect('/mycard/view')

app = webapp2.WSGIApplication([
  ('/', StartPage),
], debug=True)
