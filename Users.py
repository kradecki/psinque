
from google.appengine.api import users

def getCurrentUser():
    return users.get_current_user()
