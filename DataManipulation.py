
import logging
import vCard
import datetime
import md5

from google.appengine.ext import db

from DataModels import UserProfile, UserSettings, Permit, Group
from DataModels import UserAddress, UserEmail, UserIM, UserPhoneNumber, UserWebpage
from DataModels import Psinque, Contact, IndividualPermit, CardDAVLogin
from DataModels import PermitEmail

#-----------------------------------------------------------------------------

def generateVCard(permit):
    
    logging.info("Generating vCard")
    userProfile = permit.parent()

    newVCard = vCard.VCard()

    if(permit.canViewGivenNames):
        givenNames = userProfile.givenNames
    else:
        givenNames = u""
        
    if(permit.canViewFamilyNames):
        familyNames = userProfile.familyNames
    else:
        familyNames = u""
        
    newVCard.addNames(givenNames, familyNames)

    for email in userProfile.emails:
        permitEmail = email.individualPermits.get()
        if permitEmail.canView:
            newVCard.addEmail(email.itemValue, email.privacyType)
    
    newVCard = db.Text(newVCard.serialize())
    
    if newVCard != permit.vcard:
        logging.info("Updating vCard")
        logging.info(newVCard)
        permit.vcard = newVCard
        permit.vcardMTime = str(datetime.datetime.date(datetime.datetime.now())) + "." + str(datetime.datetime.time(datetime.datetime.now()))
        permit.vcardMD5 = md5.new(permit.vcard.encode('utf8')).hexdigest()
        
    permit.displayName = u" ".join([givenNames, familyNames])
    if permit.displayName == u"":
        for permitEmail in permit.permitEmails:
            if permitEmail.canView:
                permit.displayName = permitEmail.userEmail.email
                break
    
    permit.put()

#-----------------------------------------------------------------------------

@db.transactional
def deleteProfile(userProfileKey):

    userProfile = UserProfile.get(userProfileKey)    
    
    for e in CardDAVLogin.all().ancestor(userProfile):
        e.delete()
    for e in IndividualPermit.all().ancestor(userProfile):
        e.delete()
    for e in Permit.all().ancestor(userProfile):
        e.delete()
    for e in Psinque.all().ancestor(userProfile):
        e.delete()
    for e in Contact.all().ancestor(userProfile):
        e.delete()
    for e in Group.all().ancestor(userProfile):
        e.delete()
    for e in UserAddress.all().ancestor(userProfile):
        e.delete()
    for e in UserEmail.all().ancestor(userProfile):
        e.delete()
    for e in UserIM.all().ancestor(userProfile):
        e.delete()
    for e in UserPhoneNumber.all().ancestor(userProfile):
        e.delete()
    for e in UserWebpage.all().ancestor(userProfile):
        e.delete()
    
    if not userProfile.userSettings is None:
        userProfile.userSettings.delete()
        
    userProfile.delete()
    logging.info("User profile deleted")

#-----------------------------------------------------------------------------

def createNewPermit(userProfile, permitName, userEmail):

    permit = Permit(parent = userProfile,
                    name = permitName)
    permit.put()

    permitEmail = PermitEmail(parent = permit,
                              userEmail = userEmail)
    permitEmail.put()

    generateVCard(permit)

    logging.info("New permit created, key = " + str(permit.key()))

    return permit.key()

#-----------------------------------------------------------------------------

def createNewGroup(userProfile, groupName):

    group = Group(parent = userProfile,
                  name = groupName)
    group.put()
    logging.info("New group created, key = " + str(group.key()))

    return group.key()


#-----------------------------------------------------------------------------

@db.transactional
def createNewProfile(user):

    # Create an empty profile
    userProfile = UserProfile(user = user)
    userProfile.put()  # save the new (and empty) profile in the Datastore in order to obtain its key
    logging.info("New profile created, key = " + str(userProfile.key()))

    # User settings
    userSettings = UserSettings(parent = userProfile)
    userSettings.put()
    userProfile.userSettings = userSettings

    # Primary email address (needed for notifications, etc.)
    userEmail = UserEmail(parent = userProfile,
                          itemValue = "primary@nonexistant.com",
                          privacyType = 'Home',
                          primary = True)
    userEmail.put()

    userProfile.defaultGroup  = createNewGroup(userProfile, 'Default')
    userProfile.defaultPermit = createNewPermit(userProfile, 'Default', userEmail)
    userProfile.publicPermit  = createNewPermit(userProfile, 'Public', userEmail)

    # Save the updated user profile
    userProfile.put()

    return userProfile

#-----------------------------------------------------------------------------

