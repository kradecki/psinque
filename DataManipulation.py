
import logging
import vCard
import datetime
import md5

from google.appengine.ext import db

from DataModels import UserProfile, UserSettings, Persona, Group
from DataModels import UserAddress, UserEmail, UserIM, UserPhoneNumber, UserWebpage, UserPhoto, UserCompany, UserNickname
from DataModels import Psinque, Contact, IndividualPermit, CardDAVLogin
from DataModels import PermitEmail

#-----------------------------------------------------------------------------

def generateVCard(persona):
  
    userProfile = persona.parent()
  
    if(persona.canViewGivenNames):
        givenNames = userProfile.givenNames
    else:
        givenNames = u""
        
    if(persona.canViewFamilyNames):
        familyNames = userProfile.familyNames
    else:
        familyNames = u""
        
    displayName = u" ".join([givenNames, familyNames]).strip()
    
    if displayName != u"" and userProfile.namePrefix != u"":
        displayName = userProfile.namePrefix + u" " + displayName
    if displayName != u"" and userProfile.nameSuffix != u"":
        displayName = displayName + u", " + userProfile.nameSuffix
    
    if displayName == u"":
        for permitEmail in persona.permitEmails:
            if permitEmail.canView:
                displayName = permitEmail.userEmail.email
                break

    if displayName == u"":
        displayName = u"Anonymous user " + unicode(userProfile.key().id())
    
    persona.displayName = displayName
    persona.vcardNeedsUpdating = True
    persona.put()
    
    
def reallyGenerateVCard(persona):
    
    logging.info("Really generating vCard")
    userProfile = persona.parent()

    newVCard = vCard.VCard()

    if(persona.canViewGivenNames):
        givenNames = userProfile.givenNames
    else:
        givenNames = u""
        
    if(persona.canViewFamilyNames):
        familyNames = userProfile.familyNames
    else:
        familyNames = u""
        
    newVCard.addNames(givenNames, familyNames)

    if persona.canViewBirthday:
        birthday = userProfile.birthDate
        newVCard.addBirthday(birthday.year, birthday.month, birthday.day)

    if persona.canViewGender:
        newVCard.addGender(userProfile.gender)

    # Add company names and positions
    if persona.company:
        newVCard.addCompany(persona.company.companyName, persona.company.positionName)
    
    # Add e-mail addresses
    for email in userProfile.emails:
        individualPermit = email.individualPermits.ancestor(persona).get()
        if individualPermit.canView:
            newVCard.addEmail(email.itemValue, email.privacyType.lower())
            
    # Add IM addresses
    for im in userProfile.ims:
        individualPermit = im.individualPermits.ancestor(persona).get()
        if individualPermit.canView:
            newVCard.addIM(im.itemValue.protocol, im.privacyType.lower(), im.itemValue.address)
            
    # Add WWW addresses
    for www in userProfile.webpages:
        individualPermit = www.individualPermits.ancestor(persona).get()
        if individualPermit.canView:
            newVCard.addWebpage(www.privacyType.lower(), www.itemValue)
            
    # Add physical addresses
    for address in userProfile.addresses:
        individualPermit = address.individualPermits.ancestor(persona).get()
        if individualPermit.canView:
            newVCard.addAddress(address.privacyType,
                                u"", u"",
                                address.address,
                                address.city,
                                u"",
                                address.postalCode,
                                address.country)
    
    # Add phone numbers
    for phone in userProfile.phones:
        individualPermit = phone.individualPermits.ancestor(persona).get()
        if individualPermit.canView:
            newVCard.addPhone(phone.itemValue,
                              phone.privacyType.lower() + u"," + phone.itemType.lower())

    newVCard.addTimeStamp()
    
    newVCard = db.Text(newVCard.serialize())
    
    if newVCard != persona.vcard:
        logging.info("Updating vCard in the DataStore")
        persona.vcard = newVCard
        persona.vcardMTime = str(datetime.datetime.date(datetime.datetime.now())) + "." + str(datetime.datetime.time(datetime.datetime.now()))
        persona.vcardMD5 = md5.new(persona.vcard.encode('utf8')).hexdigest()
        
    persona.vcardNeedsUpdating = False
    persona.put()

#-----------------------------------------------------------------------------

@db.transactional
def deleteProfile(userProfileKey):

    userProfile = UserProfile.get(userProfileKey)    
    
    for e in CardDAVLogin.all().ancestor(userProfile):
        e.delete()
    for e in IndividualPermit.all().ancestor(userProfile):
        e.delete()
    for e in Persona.all().ancestor(userProfile):
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
    for e in UserPhoto.all().ancestor(userProfile):
        e.image.delete()
        e.delete()
    for e in UserNickname.all().ancestor(userProfile):
        e.delete()
    for e in UserCompany.all().ancestor(userProfile):
        e.delete()
    for e in UserWebpage.all().ancestor(userProfile):
        e.delete()
    
    if not userProfile.userSettings is None:
        userProfile.userSettings.delete()
        
    userProfile.delete()
    logging.info("User profile deleted")

#-----------------------------------------------------------------------------

def createNewPersona(userProfile, personaName, userEmail):

    persona = Persona(parent = userProfile,
                    name = personaName)
    persona.put()

    permitEmail = PermitEmail(parent = persona,
                              userEmail = userEmail)
    permitEmail.put()

    generateVCard(persona)

    logging.info("New persona created, key = " + str(persona.key()))

    return persona.key()

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
                          itemValue = user.email(),  # "primary@nonexistant.com"
                          privacyType = 'Home',
                          primary = True)
    userEmail.put()

    userProfile.defaultGroup  = createNewGroup(userProfile, 'Default')
    userProfile.defaultPersona = createNewPersona(userProfile, 'Default', userEmail)
    userProfile.publicPersona  = createNewPersona(userProfile, 'Public', userEmail)
    
    userProfile.pseudonyms = [ user.nickname() ]

    # Save the updated user profile
    userProfile.put()

    return userProfile

#-----------------------------------------------------------------------------

