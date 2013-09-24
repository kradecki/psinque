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

    def work(self):
        self.sendContent('templates/Static_Work.html')

    def help(self):
        self.sendContent('templates/Static_Help.html')

    def ios(self):
        self.sendContent('templates/Static_Help_iOS.html')

    def android(self):
        self.sendContent('templates/Static_Help_Android.html')

    def windows(self):
        self.sendContent('templates/Static_Help_Windows.html')

#-----------------------------------------------------------------------------

app = webapp2.WSGIApplication([
    (r'/static/(\w+)', StaticPageHandler),
], debug=True)
