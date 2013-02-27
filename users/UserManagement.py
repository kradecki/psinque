# -*- coding: utf-8 -*-

"""
.. moduleauthor:: Stanisław Raczyński <sutashu@gmail.com>
.. module:: users
   :synopsis: Back-end for all user data management.
"""

import logging

from UserDataModels import UserSettings, CardDAVPassword

def groupList(user):
    """Returns the list of all groups created by the logged in user.

    :returns: list -- the list of groups

    """
    return ["public"]  # for now only all users are in the public group

def friendList(user, group):
    if group == "public":
        return ["0123456789"]  # to test CardDAV
    else:
        return []

def generateVCard(userID):
    if userID == "0123456789":
        return u"""
BEGIN:VCARD
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
END:VCARD
"""
    else:
        return ""

#TODO: Query by key is faster
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
