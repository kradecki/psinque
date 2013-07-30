# -*- coding: utf-8 -*-

import webapp2

from google.appengine.api import users

from MasterHandler import StaticHandler

#-----------------------------------------------------------------------------

directOpenIDProviders = [
    'https://www.google.com/accounts/o8/id',
    'yahoo.com',
    'yahoo.co.jp',
]

directOpenIDIconNames = ['google', 'yahoo', 'yahoo_japan']

#-----------------------------------------------------------------------------

class StaticPageHandler(StaticHandler):

    #****************************
    # Views
    #

    def landing(self):
      
        self.sendContent('templates/Landing.html', {
            'loginurls': zip([users.create_login_url(dest_url = '/mycard/view',
                                                     federated_identity = uri)
                             for uri in directOpenIDProviders],
                             directOpenIDIconNames)
        })


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
