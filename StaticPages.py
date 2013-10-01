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

    def pricing(self):
        self.sendContent('templates/Static_Pricing.html')

    def helpgeneral(self):
        self.sendContent('templates/Static_Help.html')

    def helpoverview(self):
        self.sendContent('templates/Static_Help_Overview.html')

    def helpios(self):
        self.sendContent('templates/Static_Help_iOS.html')

    def helpandroid(self):
        self.sendContent('templates/Static_Help_Android.html')

    def helpwindows(self):
        self.sendContent('templates/Static_Help_Windows.html')

    def helpprofile(self):
        self.sendContent('templates/Static_Help_Profile.html')

    def helppersonas(self):
        self.sendContent('templates/Static_Help_Personas.html')

    def helppsinques(self):
        self.sendContent('templates/Static_Help_Psinques.html')

#-----------------------------------------------------------------------------

app = webapp2.WSGIApplication([
    (r'/static/(\w+)', StaticPageHandler),
], debug=True)
