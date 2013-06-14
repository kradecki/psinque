# -*- coding: utf-8 -*-

from google.appengine.api import mail
from google.appengine.api import users

def getPrimaryEmail(userProfile):
    
    return userProfile.emails.filter("primary =", True).get().email


def createAcceptUrl(psinque):
    
    return "http://psinque.appspot.com/psinques/acceptpsinque?key=" + str(psinque.key())


def createRejectUrl(psinque):
    
    return "http://psinque.appspot.com/psinques/rejectpsinque?key=" + str(psinque.key())


def sendNotification(psinque, subject, body):
    
    message = mail.EmailMessage(sender="Psinque notifications <noreply@psinque.appspotmail.com>",
                                subject=subject)
    fromUser = psinque.fromUser
    message.to = getPrimaryEmail(fromUser)
    message.body = body
    message.send()


def notifyPendingPsinque(psinque):
    
    sendNotification(psinque, 
                     "You have a new pending psinque request",
                     u"""Dear %s:

Another user, %s, has requested access to your private contact
details.

Please click <a href="%s">this link</a> to accept this psinque.

Please click <a href="%s">this link</a> to reject this psinque.

The Psinque Team
""" % (u" ".join(psinque.fromUser.givenNames),
       psinque.parent().parent().defaultPermit.displayName,
       createRejectUrl(psinque),
       createAcceptUrl(psinque)))

    
def notifyStoppedUsingPrivateData(psinque):
    
    pass


def notifyDowngradedPsinque(psinque):
    
    pass


def notifyStoppedUsingPrivateData(psinque):
    
    sendNotification(psinque, 
                     "%s has stopped using your private data" % psinque.fromUser.fullName,
                     u"""Dear %s:

Another user, %s, has stopped using your private data.

The Psinque Team
""" % (psinque.fromUser.fullName,
       psinque.displayName))

    
def notifyDowngradedPsinque(psinque):
    
    sendNotification(psinque, 
                     "Your access to private data has been revoked",
                     u"""Dear %s:

Another user, %s, has revoked your access to his/her private data.

The Psinque Team
""" % (u" ".join(psinque.parent().parent().givenNames),
       psinque.displayName))


def notifyAcceptedRequest(psinque):
    
    sendNotification(psinque, 
                     "Your request for sharing private contact data has been accepted",
                     u"""Dear %s:

Another user, %s, has accepted your request for sharing private contact data.

The Psinque Team
""" % (u" ".join(psinque.parent().parent().givenNames),
       psinque.displayName))

    
def notifyRejectedRequest(psinque):
    
    sendNotification(psinque, 
                     "Your request for sharing private contact data has been rejected",
                     u"""Dear %s:

Another user, %s, has rejected your request for sharing private contact data.

The Psinque Team
""" % (u" ".join(psinque.parent().parent().givenNames),
       psinque.displayName))
