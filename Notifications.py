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

acceptTemplate    = jinja_environment.get_template("templates/emails/Accept.html")
rejectTemplate    = jinja_environment.get_template("templates/emails/Reject.html")
downgradeTemplate = jinja_environment.get_template("templates/emails/Downgrade.html")
stopTemplate      = jinja_environment.get_template("templates/emails/Stop.html")
pendTemplate      = jinja_environment.get_template("templates/emails/Pend.html")
activeTemplate    = jinja_environment.get_template("templates/emails/AccountActive.html")

#-----------------------------------------------------------------------------

psinqueSender = "Psinque notifications <noreply@psinque.appspotmail.com>"

def getPrimaryEmail(userProfile):
    
    return userProfile.emails.filter("primary =", True).get().itemValue


def sendNotification(userProfile, subject, html, shorttext = u""):
    
    message = mail.EmailMessage(sender = psinqueSender,
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
    sender     = psinque.parent().parent()
    
    sendNotification(receipient, 
                     "You have a new pending psinque request",
                     pendTemplate.render({
                         'receipientsName': receipient.displayName,
                         'friendsName': sender.displayName,
                         'acceptURL': "http://www.psinque.com/psinques/acceptrequest?key=" + str(psinque.key()) + "&redirect=true",
                         'rejectURL': "http://www.psinque.com/psinques/rejectrequest?key=" + str(psinque.key()) + "&redirect=true",
                     }))

    
def notifyStoppedUsingPrivateData(psinque):
    
    receipient = psinque.fromUser
    sender     = psinque.parent().parent()

    sendNotification(receipient, 
                     "%s has stopped using your private data" % sender.displayName,
                     stopTemplate.render({
                         'receipientsName': receipient.displayName,
                         'friendsName': sender.displayName,
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


# Invitation to join Psinque ------------------------------------------------


def notifyAccountActive(email, recipientsName):
   
    message = mail.EmailMessage(sender = psinqueSender,
                                subject = "Your Psinque account has been activated")
    message.to = email
    message.html = activeTemplate.render()
    message.send()


def notifyInvitation(email):

    message = mail.EmailMessage(sender = psinqueSender,
                                subject = "Invitation to join Psinque")
    message.to = email
    message.html = rejectTemplate.render({
                         'receipientsName': receipient.displayName,
                         'friendsName': psinque.displayName,
                   })
    message.send()


def inviteToPsinque(email):
    
    existingEmail = UserEmail.all().filter("itemValue =", email).get()
    
    if not existingEmail is None:
      
        userProfile = existingEmail.parent()
        
        if not userProfile.active:
            
            userProfile.active = True
            userProfile.put()
            
            notifyAccountActive(email)
            
            return True  # profile activated
         
        else:
            
            return False   # user already active
    else:
      
        invitation = Invitation(email = email)
        invitation.put()
        
        notifyInvitation(email)
        
        return True


#-----------------------------------------------------------------------------
