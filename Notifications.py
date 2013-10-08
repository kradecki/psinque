# -*- coding: utf-8 -*-

import os
import jinja2

from google.appengine.api import mail
from google.appengine.api import users

from DataModels import Notification

#-----------------------------------------------------------------------------

jinja_environment = jinja2.Environment(
    loader = jinja2.FileSystemLoader(os.path.dirname(__file__))
)

#-----------------------------------------------------------------------------

bodyHeader = u"""Dear %s:

"""

bodyFooter = u"""
Sincerely,
The Psinque Team
"""

bodyPendingPsinque = bodyHeader + \
                     u"""Another user, %s, has requested access to your private contact
details.

Please click <a href="%s">this link</a> to accept this psinque.

Please click <a href="%s">this link</a> to reject this psinque.""" + \
                     bodyFooter


bodyStoppedUsingPrivateData = bodyHeader + \
                              u"""Another user, %s, has stopped using your private data.""" + \
                              bodyFooter

bodyDowngradedPsinque = bodyHeader + \
                        u"""Another user, %s, has revoked your access to his/her private data.""" + \
                        bodyFooter

bodyAcceptedRequest = bodyHeader + \
                      u"""Another user, %s, has accepted your request for sharing private contact data.""" + \
                      bodyFooter

bodyRejectedRequest = bodyHeader + \
                      u"""Another user, %s, has rejected your request for sharing private contact data.""" + \
                      bodyFooter

#-----------------------------------------------------------------------------

def getPrimaryEmail(userProfile):
    
    return userProfile.emails.filter("primary =", True).get().itemValue


def createAcceptUrl(psinque):
    
    return "http://www.psinque.com/psinques/acceptrequest?key=" + str(psinque.key())


def createRejectUrl(psinque):
    
    return "http://www.psinque.com/psinques/rejectrequest?key=" + str(psinque.key())


def sendNotification(user, subject, body, shorttext = u""):
    
    message = mail.EmailMessage(sender = "Psinque notifications <noreply@psinque.appspotmail.com>",
                                subject = subject)
    message.to = getPrimaryEmail(user)
    message.body = body
    message.html = body
    message.send()
    
    #if shorttext != u"":
        #onpageNotification = Notification(parent = user,
                                          #text = shorttext)
        #onpageNotification.put()

#-----------------------------------------------------------------------------

def notifyPendingPsinque(psinque):
    
    acceptURL = createAcceptUrl(psinque)
    rejectURL = createRejectUrl(psinque)
    
    sendNotification(psinque.fromUser, 
                     "You have a new pending psinque request",
                     bodyPendingPsinque % (psinque.fromUser.givenNames,
                                           psinque.parent().parent().defaultPersona.displayName,
                                           acceptURL, rejectURL),
                     u"You have a pending psinque request from ...")
    
    #template = jinja_environment.get_template(templateName)
    #body = template.render({'what': 'value'})

    
def notifyStoppedUsingPrivateData(psinque):
    
    sendNotification(psinque.fromUser, 
                     "%s has stopped using your private data" % psinque.fromUser.fullName,
                     bodyStoppedUsingPrivateData % (psinque.fromUser.fullName,
                     psinque.displayName))

    
def notifyDowngradedPsinque(psinque):
    
    sendNotification(psinque.fromUser, 
                     "Your access to private data has been revoked",
                     bodyDowngradedPsinque % (psinque.parent().parent().givenNames,
                                              psinque.displayName))


def notifyAcceptedRequest(psinque):
    
    sendNotification(psinque.fromUser, 
                     "Your request for sharing private contact data has been accepted",
                     bodyAcceptedRequest % (psinque.parent().parent().givenNames,
                                            psinque.displayName))

    
def notifyRejectedRequest(psinque):
    
    sendNotification(psinque.fromUser, 
                     "Your request for sharing private contact data has been rejected",
                     bodyRejectedRequest % (psinque.parent().parent().givenNames,
                                            psinque.displayName))

#-----------------------------------------------------------------------------
