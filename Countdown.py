# -*- coding: utf-8 -*-

import webapp2
import os
import jinja2

jinja_environment = jinja2.Environment(
    loader = jinja2.FileSystemLoader(os.path.dirname(__file__)))


class StartPage(webapp2.RequestHandler):
  
    def get(self):
      
        template = jinja_environment.get_template('templates/countdown.html')
        self.response.out.write(template.render({}))

app = webapp2.WSGIApplication([
    ('/', StartPage),
], debug=True)
