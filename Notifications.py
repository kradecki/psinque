# -*- coding: utf-8 -*-

import os
import jinja2
import logging

from google.appengine.api import mail
from google.appengine.api import users

from DataModels import Notification

#-----------------------------------------------------------------------------

jinja_environment = jinja2.Environment(
    loader = jinja2.FileSystemLoader(os.path.dirname(__file__))
)

acceptTemplate    = jinja_environment.get_template("templates/Email_Accept.html")
rejectTemplate    = jinja_environment.get_template("templates/Email_Reject.html")
downgradeTemplate = jinja_environment.get_template("templates/Email_Downgrade.html")
stopTemplate      = jinja_environment.get_template("templates/Email_Stop.html")
pendTemplate      = jinja_environment.get_template("templates/Email_Pend.html")

#-----------------------------------------------------------------------------

def getPrimaryEmail(userProfile):
    
    return userProfile.emails.filter("primary =", True).get().itemValue


def sendNotification(userProfile, subject, html, shorttext = u""):
    
    logging.info("sendNotification()")
    logging.info(html)
    
    message = mail.EmailMessage(sender = "Psinque notifications <noreply@psinque.appspotmail.com>",
                                subject = subject)
    message.to = getPrimaryEmail(userProfile)
    #message.body = html
    message.html = html
    message.send()
    
    #if shorttext != u"":
        #onpageNotification = Notification(parent = user,
                                          #text = shorttext)
        #onpageNotification.put()

#-----------------------------------------------------------------------------


# Notifications for the sending user -----------------------------------------


def notifyPendingPsinque(psinque):
    
    receipient = psinque.fromUser
    
    sendNotification(receipient, 
                     "You have a new pending psinque request",
                     pendTemplate.render({
                         'receipientsName': receipient.displayName,
                         'friendsName': psinque.parent().displayName,
                         'acceptURL': "http://www.psinque.com/psinques/acceptrequest?key=" + str(psinque.key()),
                         'rejectURL': "http://www.psinque.com/psinques/rejectrequest?key=" + str(psinque.key()),
                     }))

    
def notifyStoppedUsingPrivateData(psinque):
    
    receipient = psinque.fromUser

    sendNotification(receipient, 
                     "%s has stopped using your private data" % psinque.parent().displayName,
                     stopTemplate.render({
                         'receipientsName': receipient.displayName,
                         'friendsName': psinque.parent().displayName,
                     }))


# Notifications for the receiving user ---------------------------------------


def notifyDowngradedPsinque(psinque):
    
    receipient = psinque.parent().parent()

    sendNotification(receipient, 
                     "Your access to private data has been revoked",
                     downgradeTemplate.render({
                         'receipientsName': receipient.displayName,
                         'friendsName': psinque.displayName,
                     }))


def notifyAcceptedRequest(psinque):
  
    receipient = psinque.parent().parent()
        
    sendNotification(receipient, 
                     "Your request for private contact data has been accepted",
                     acceptTemplate.render({
                         'receipientsName': receipient.displayName,
                         'friendsName': psinque.displayName,
                     }))

    
def notifyRejectedRequest(psinque):
    
    receipient = psinque.parent().parent()

    sendNotification(psinque.fromUser, 
                     "Your request for sharing private contact data has been rejected",
                     rejectTemplate.render({
                         'receipientsName': receipient.displayName,
                         'friendsName': psinque.displayName,
                     }))

#-----------------------------------------------------------------------------
