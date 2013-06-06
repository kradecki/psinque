# -*- coding: utf-8 -*-

import logging

class VCard():
    
    def __init__(self):

        self.vcardTest = u"BEGIN:VCARD\nVERSION:4.0\n"

    def addNames(self, givenNames,
                       familyNames,
                       additionalNames = "",
                       honorificPrefixes = "",
                       honorificSuffixes = ""):
        
        self.vcardTest += u"N:" + \
                          familyNames + u";" + \
                          givenNames + u";" + \
                          additionalNames + u";" + \
                          honorificPrefixes + u";" + \
                          honorificSuffixes + u"\n"
                 
        self.vcardTest += u"FN:"
        
        if honorificPrefixes != "":
            self.vcardTest += honorificPrefixes + u" "
                
        self.vcardTest += givenNames + u" " + familyNames

        if additionalNames != "":
            self.vcardTest += u" " + additionalNames

        if honorificSuffixes != "":
            self.vcardTest += u", "+ honorificSuffixes
            
        self.vcardTest += u"\n"

    
    def addEmail(self, email, emailType):
    
        self.vcardTest += u"EMAIL;" + emailType + u":" + email + u"\n"
        
    
    def serialize(self):
            
        return self.vcardTest + u"END:VCARD"
