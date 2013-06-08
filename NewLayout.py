# -*- coding: utf-8 -*-

import os
import webapp2
import jinja2

jinja_environment = jinja2.Environment(
    loader = jinja2.FileSystemLoader(os.path.dirname(__file__)))

class NewLayout(webapp2.RequestHandler):
  def get(self):
    self.response.out.write(jinja_environment.get_template("templates/newlayout.html").render())

app = webapp2.WSGIApplication([
  ('/newlayout', NewLayout),
], debug=True)
