
import os
import logging

from google.appengine.ext import webapp
from google.appengine.api import users
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.ext.webapp import template

from MasterHandler import MasterHandler

class Notifications(MasterHandler):
  def get(self):
    MasterHandler.sendTopTemplate(self, activeEntry = "Notifications")
    self.response.out.write('<div id="content">Under construction</div>')
    MasterHandler.sendBottomTemplate(self)

application = webapp.WSGIApplication([
  ('/notifications', Notifications),
], debug=True)

def main():
  run_wsgi_app(application)

if __name__ == '__main__':
  main()
