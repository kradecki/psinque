# -*- coding: utf-8 -*-

import webapp2

class StartPage(webapp2.RequestHandler):
  
    def get(self):
      
        self.redirect('/profile/view')

app = webapp2.WSGIApplication([
    ('/reallandingforsecrettesters', StartPage),
], debug=True)
