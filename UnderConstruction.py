
import os
import logging
import webapp2

from MasterHandler import MasterHandler

class Groups(MasterHandler):
  def get(self):
    MasterHandler.sendTopTemplate(self, activeEntry = "Groups")
    self.response.out.write('<div id="content">Under construction</div>')
    MasterHandler.sendBottomTemplate(self)

application = webapp2.WSGIApplication([
              ('/groups', Groups),
              ], debug=True)

#def main():
  #webapp2.run_wsgi_app(application)

#if __name__ == '__main__':
  #main()
