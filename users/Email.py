
from google.appengine.api import mail

from users.UserManagement import getPrimaryEmail, getDisplayNameFromPsinque

def notifyPendingPsinque(psinque):
    message = mail.EmailMessage(sender="Psinque notifications <noreply@psinque.appspotmail.com>",
                                subject="You have a new pending psinque request")
    fromUser = psinque.fromUser
    message.to = getPrimaryEmail(fromUser)
    
    message.body=u"""
Dear %s:

Another user, %s, has requested access to your private contact
details. Please click the following link to make a decision 

The Psinque Team
""" % (fromUser.firstname + " " + fromUser.lastname, getDisplayNameFromPsinque(psinque))

    message.send()