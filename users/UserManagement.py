# -*- coding: utf-8 -*-

"""
.. moduleauthor:: Stanisław Raczyński <sutashu@gmail.com>
.. module:: users
   :synopsis: Back-end for all user data management.
"""

import logging

import vobject

from UserDataModels import UserSettings, UserGroup, CardDAVPassword

def groupList(user):
    """Returns the list of all groups created by the logged in user.

    :returns: list -- the list of groups

    """
    return ["public"]  # for now only all users are in the public group


def friendList(user, group):
    if group == "public":
        return ["0123456789.vcf", "0123456790.vcf"]  # to test CardDAV
    else:
        return []


def generateVCard(user, friendID):
    if friendID == "0123456789":
        return u"""BEGIN:VCARD
VERSION:3.0
N:guy;Some;;;
FN:Some idiot
TEL;TYPE=CELL:55512345678
PRODID:-//dmfs.org//mimedir.vcard//EN
REV:20130418T163727Z
UID:0df20478-2428-415d-9ffb-f3f69a1bceb1
X-RADICALE-NAME:0df20478-2428-415d-9ffb-f3f69a1bceb1.vcf
END:VCARD"""
    if friendID == "0123456790":
        return u"""BEGIN:VCARD
VERSION:2.1
N:Gump;Forrest
FN:Forrest Gump
ORG:Bubba Gump Shrimp Co.
TITLE:Shrimp Man
PHOTO;GIF:http://www.example.com/dir_photos/my_photo.gif
TEL;WORK;VOICE:(111) 555-1212
TEL;HOME;VOICE:(404) 555-1212
ADR;WORK:;;100 Waters Edge;Baytown;LA;30314;United States of America
LABEL;WORK;ENCODING=QUOTED-PRINTABLE:100 Waters Edge=0D=0ABaytown, LA 30314=0D=0AUnited States of America
ADR;HOME:;;42 Plantation St.;Baytown;LA;30314;United States of America
LABEL;HOME;ENCODING=QUOTED-PRINTABLE:42 Plantation St.=0D=0ABaytown, LA 30314=0D=0AUnited States of America
EMAIL;PREF;INTERNET:forrestgump@example.com
REV:20080424T195243Z
END:VCARD"""
    return ""


def getPrimaryEmail(user):
    return user.emails.ancestor(user.key()).filter("primary =", True).get().email


def getName(user):
    return user.firstName + " " + user.lastName


def getPublicGroup(user):
    publicGroup = UserGroup.all(keys_only = True)
    publicGroup.ancestor(user.key())
    publicGroup.filter("name =", "Public")
    return publicGroup.get()


def getIncomingDisplayNameFromPsinque(psinque):
    publicGroupKey = getPublicGroup(psinque.fromUser)
    if UserGroup.get(publicGroupKey).canViewName:
        return getName(psinque.fromUser)
    for group in psinque.groups:
        if group and group.canViewName:
            return getName(psinque.fromUser)
    return getPrimaryEmail(psinque.fromUser)


def getOutgoingDisplayNameFromPsinque(psinque):
    publicGroupKey = getPublicGroup(psinque.toUser)
    if UserGroup.get(publicGroupKey).canViewName:
        return getName(psinque.toUser)
    for group in psinque.groups:
        if group and group.canViewName:
            return getName(psinque.toUser)
    return getPrimaryEmail(psinque.toUser)


def getDisplayName(user, toUser):
    
    if not getPublicGroup(fromUser).canViewName: # Perhaps the name is visible to everyone?  
        psinque = Psinque.all().filter("toUser =", toUser).filter("fromUser =", user).get()
        primaryEmail = getPrimaryEmail(user)
        if (len(psinque) == 0) or (psinque.status != "Established") or (not psinque.group.canViewName):
            return primaryEmail    # email address is always visible
    return getName(user)
    

def getUserSettings(user):
    return UserSettings.all().filter("user =", user).get()


#TODO: Set up generated password indexes
def cardDAVPassword(username):
    password = CardDAVPassword.all().filter("generatedUsername =", username).get()
    if not password:  # no user profile registered yet
        return None
    if not getUserSettings(password.user).cardDAVenabled: # this can happen if the user's disabled CardDAV, but somehow the passwords is still here
        password.delete()
        return False
    return password.generatedPassword

def cardDAVUser(username):
    password = CardDAVPassword.all().filter("generatedUsername =", username).get()
    if not password:
        return None
    return password.user
