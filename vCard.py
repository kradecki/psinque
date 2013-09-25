# -*- coding: utf-8 -*-

import logging

class VCard():
    
    def __init__(self):

        self.vcardString = u"BEGIN:VCARD\nVERSION:3.0\n"

    def addNames(self, givenNames,
                       familyNames,
                       additionalNames = u"",
                       honorificPrefixes = u"",
                       honorificSuffixes = u""):
        
        self.vcardString += u"N:" + \
                          familyNames + u";" + \
                          givenNames + u";" + \
                          additionalNames + u";" + \
                          honorificPrefixes + u";" + \
                          honorificSuffixes + u"\n"
                 
        self.vcardString += u"FN:"
        
        if honorificPrefixes != u"":
            self.vcardString += honorificPrefixes + u" "
                
        self.vcardString += givenNames + u" " + familyNames

        if additionalNames != u"":
            self.vcardString += u" " + additionalNames

        if honorificSuffixes != u"":
            self.vcardString += u", "+ honorificSuffixes
            
        self.vcardString += u"\n"

    
    def addEmail(self, email, emailType):
    
        self.vcardString += u"EMAIL;TYPE=" + emailType + u":" + email + u"\n"
        
        
    def addAddress(self, addressType, poBox, extAddress, street,
                         locality, region, postalCode, country):
      
        label = street
        if extAddress != u"":
            label += u" " + extAddress
        if postalCode != u"":
            label += u", " + postalCode
            if locality != u"":
                label += u" " + locality
        elif locality != u"":
            label += u", " + locality
        if country != u"":
            label += u", " + country
      
        self.vcardString += u"ADR;TYPE=" + addressType + \
                          u";LABEL=\"" + label + u"\"\n  :" + \
                          poBox + u";" + \
                          extAddress + u";" + \
                          street + u";" + \
                          locality + u";" + \
                          region + u";" + \
                          postalCode + u";" + \
                          country + u"\n"
        
    
    def addPhone(self, phone, phoneType):
      
        #self.vcardString += u"TEL;TYPE=" + phoneType + ";VALUE=uri:tel:" + phone + u"\n"
        self.vcardString += u"TEL;TYPE=" + phoneType + u":" + phone + u"\n"
        
    
    def addIM(self, imtype, privacytype, imaddress):
        
        if imtype == "http://talk.google.com/":
            self.vcardString += u"X-GOOGLE-TALK;TYPE=" + privacytype + u":" + imaddress + u"\n"
        elif imtype == "http://www.skype.com/":
            self.vcardString += u"X-SKYPE;TYPE=" + privacytype + u":" + imaddress + u"\n"
        elif imtype == "http://gadu-gadu.pl/":
            self.vcardString += u"X-GADUGADU;TYPE=" + privacytype + u":" + imaddress + u"\n"
        elif imtype == "http://messenger.msn.com/":
            self.vcardString += u"IMPP;TYPE=" + privacytype + u":msn:" + imaddress + u"\n"
        elif imtype == "http://messenger.yahoo.com/":
            self.vcardString += u"IMPP;TYPE=" + privacytype + u":ymsgr:" + imaddress + u"\n"
        
    
    def addWebpage(self, privacytype, url):
        
        self.vcardString += u"URL;TYPE=" + privacytype + u":" + url + u"\n"
      
      
    def addCompany(self, company, position):
        self.vcardString += u"ORG:" + company + u"\n"
        self.vcardString += u"TITLE:" + position + u"\n"
      
      
    def addTimeStamp(self, timestamp):
      
        self.vcardString += u"REV:" + timestamp + u"\n"
        
    
    def serialize(self):
            
        return self.vcardString + u"END:VCARD\n"
