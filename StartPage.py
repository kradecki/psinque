# -*- coding: utf-8 -*-

import os
import webapp2
import jinja2

from Users import getCurrentUser

jinja_environment = jinja2.Environment(
    loader = jinja2.FileSystemLoader(os.path.dirname(__file__)))


class StartPage(webapp2.RequestHandler):
  
    def get(self):
      
        self.redirect('/mycard/view')

app = webapp2.WSGIApplication([
    ('/', StartPage),
], debug=True)
