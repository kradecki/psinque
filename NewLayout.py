# -*- coding: utf-8 -*-

import os
import webapp2
import jinja2

jinja_environment = jinja2.Environment(
    loader = jinja2.FileSystemLoader(os.path.dirname(__file__)))

class MenuEntry:
    url = ""
    title = ""
    entryclass = ""
    def __init__(self, url, title, entryclass = ""):
        self.url = url
        self.title = title
        self.entryclass = entryclass

class NewLayout(webapp2.RequestHandler):
  def get(self):
    self.response.out.write(jinja_environment.get_template("templates/newlayout.html").render(menuentries = [
            MenuEntry("mycard/view", "My card"),
            MenuEntry("permits/view", "Permits"),
            MenuEntry("psinques/view", "Psinques"),
    ]))

app = webapp2.WSGIApplication([
  ('/newlayout', NewLayout),
], debug=True)
