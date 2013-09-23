# -*- coding: utf-8 -*-

import webapp2

from MasterHandler import StaticHandler

class StaticPageHandler(StaticHandler):

    #****************************
    # Views
    #


    def about(self):
      
        self.sendContent('templates/Static_AboutUs.html')


    def terms(self):
      
        self.sendContent('templates/Static_Terms.html')


    def privacy(self):
      
        self.sendContent('templates/Static_Privacy.html')


    def help(self):
      
        self.sendContent('templates/Static_Help.html')


    def work(self):
      
        self.sendContent('templates/Static_Work.html')


#-----------------------------------------------------------------------------

app = webapp2.WSGIApplication([
    (r'/static/(\w+)', StaticPageHandler),
], debug=True)
