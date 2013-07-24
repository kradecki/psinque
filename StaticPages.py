# -*- coding: utf-8 -*-

import webapp2

from MasterHandler import MasterHandler

#-----------------------------------------------------------------------------

class StaticPageHandler(MasterHandler):

    #****************************
    # Views
    #

    def faq(self):
      
        self.sendContent('templates/FAQ.html')


    def about(self):
      
        self.sendContent('templates/AboutUs.html')

#-----------------------------------------------------------------------------

app = webapp2.WSGIApplication([
    (r'/static/(\w+)', StaticPageHandler),
], debug=True)
