
from google.appengine.api import mail

from users.UserManagement import getPrimaryEmail, getOutgoingDisplayNameFromPsinque

def createAcceptUrl(psinque):
    return "http://psinque.appspot.com/outgoing/acceptpsinque?key=" + str(psinque.key())

def createRejectUrl(psinque):
    return "http://psinque.appspot.com/outgoing/rejectpsinque?key=" + str(psinque.key())

def notifyPendingPsinque(psinque):
    message = mail.EmailMessage(sender="Psinque notifications <noreply@psinque.appspotmail.com>",
                                subject="You have a new pending psinque request")
    fromUser = psinque.fromUser
    message.to = getPrimaryEmail(fromUser)
    
    message.body=u"""
Dear %s:

Another user, %s, has requested access to your private contact
details.

Please click <a href="%s">this link</a> to reject this psinque.

Please click <a href="%s">this link</a> to accept this psinque.

The Psinque Team
""" % (fromUser.firstName + " " + fromUser.lastName,
       getOutgoingDisplayNameFromPsinque(psinque),
       createRejectUrl(psinque),
       createAcceptUrl(psinque))

    message.send()
    
def notifyStoppedUsingPrivateData(psinque):
    pass

def notifyDowngradedPsinque(psinque):
    pass