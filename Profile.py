class ViewProfile(MasterHandler):

  def get(self):
    user = users.get_current_user()
    query = UserProfile.all()
    userProfile = query.filter("user =", user).get()
    if not userProfile:  # no user profile registered yet, so ask user to create his profile
      self.redirect("/editprofile")  # and redirect to edit the profile
      return

    template_values = {
      'firstname': userProfile.firstname,
      'lastname': userProfile.lastname,
    }
    MasterHandler.sendTopTemplate(self, activeEntry = "Visiting card")
    MasterHandler.sendContent(self, 'templates/viewProfile.html', template_values)
    MasterHandler.sendBottomTemplate(self)

class EditProfile(MasterHandler):

  def get(self):   # form for editing details
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
  ('/profile', ViewProfile),
  ('/editprofile', EditProfile),
  ('/submitprofile', EditProfile)
], debug=True)

def main():
  run_wsgi_app(application)

if __name__ == '__main__':
  main()
