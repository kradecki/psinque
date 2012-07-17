
import os
import logging

from google.appengine.ext import webapp
from google.appengine.api import users
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.ext.webapp import template

from MasterHandler import MasterHandler

from UserDataModels import UserProfile, UserSettings, availableLanguages

class StartPage(webapp.RequestHandler):
  def get(self):
    user = users.get_current_user()
    if not user:    # user not logged in
        self.redirect("/login")
    else:
        self.redirect('/profile')

class Login(webapp.RequestHandler):
  def get(self):
    self.response.out.write(template.render(os.path.join(os.path.dirname(__file__), "templates/login.html"),
                                            {'loginurl': users.create_login_url("/profile")}
                                           ))

class ViewProfile(MasterHandler):

  def get(self):
    user = users.get_current_user()
    query = UserProfile.all()
    userProfile = query.filter("user =", user).get()
    if not userProfile:  # no user profile registered yet, so create a new one
      userProfile = UserProfile()
      userProfile.user = user
      userProfile.put()  # save the new (and empty) profile in the Datastore
      userSettings = UserSettings()
      userSettings.preferredLanguage = availableLanguages[0]  # select the default language
      userSettings.notifyOnNewsletter = True
      userSettings.user = user
      userSettings.put()

    template_values = {
      'firstname': userProfile.firstname,
      'lastname': userProfile.lastname,
    }
    MasterHandler.sendTopTemplate(self, activeEntry = "Visiting card")
    MasterHandler.sendContent(self, 'templates/viewProfile.html', template_values)
    MasterHandler.sendBottomTemplate(self)

class EditProfile(MasterHandler):

  def get(self):   # form for editing details
    MasterHandler.sendTopTemplate(self, activeEntry = "Visiting card")
    MasterHandler.sendContent(self, 'templates/editProfile.html', None)
    MasterHandler.sendBottomTemplate(self)

  def post(self):  # executed when the user hits the 'Save' button, which sends a POST request
    user = users.get_current_user()
    query = UserProfile.all()
    userProfile = query.filter("user =", user).get()
    userProfile.firstname = self.request.get('firstname')
    userProfile.lastname = self.request.get('lastname')
    userProfile.put()

    self.redirect('/profile')  # redirects to ViewProfile

application = webapp.WSGIApplication([
  ('/', StartPage),
  ('/login', Login),
  ('/profile', ViewProfile),
  ('/editprofile', EditProfile),
  ('/submitprofile', EditProfile)
], debug=True)

def main():
  run_wsgi_app(application)

if __name__ == '__main__':
  main()
