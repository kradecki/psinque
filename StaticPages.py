# -*- coding: utf-8 -*-

import webapp2

from MasterHandler import StaticHandler

class StaticPageHandler(StaticHandler):

    #****************************
    # Views
    #

    def about(self):
        self.sendContent('templates/static/AboutUs.html')

    def terms(self):
        self.sendContent('templates/static/Terms.html')

    def privacy(self):
        self.sendContent('templates/static/Privacy.html')

    def work(self):
        self.sendContent('templates/static/Work.html')

    def pricing(self):
        self.sendContent('templates/static/Pricing.html')

    def helpgeneral(self):
        self.sendContent('templates/static/Help.html')

    def helpoverview(self):
        self.sendContent('templates/static/Help_Overview.html')

    def helpios(self):
        self.sendContent('templates/static/Help_iOS.html')

    def helpandroid(self):
        self.sendContent('templates/static/Help_Android.html')

    def helpwindows(self):
        self.sendContent('templates/static/Help_Windows.html')

    def helpprofile(self):
        self.sendContent('templates/static/Help_Profile.html')

    def helppersonas(self):
        self.sendContent('templates/static/Help_Personas.html')

    def helppsinques(self):
        self.sendContent('templates/static/Help_Psinques.html')

#-----------------------------------------------------------------------------

app = webapp2.WSGIApplication([
    (r'/static/(\w+)', StaticPageHandler),
], debug=True)
