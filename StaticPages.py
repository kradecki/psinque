# -*- coding: utf-8 -*-

import webapp2

from MasterHandler import StaticHandler

class StaticPageHandler(StaticHandler):

    #****************************
    # Views
    #

    def faq(self):
      
        self.sendContent('templates/FAQ.html')


    def about(self):
      
        self.sendContent('templates/AboutUs.html')


    def investors(self):
      
        self.sendContent('templates/Investors.html')


    def privacy(self):
      
        self.sendContent('templates/Privacy.html')


    def terms(self):
      
        self.sendContent('templates/Terms.html')


    def mobile(self):
      
        self.sendContent('templates/Mobile.html')


    def support(self):
      
        self.sendContent('templates/Support.html')


#-----------------------------------------------------------------------------

app = webapp2.WSGIApplication([
    (r'/static/(\w+)', StaticPageHandler),
], debug=True)
