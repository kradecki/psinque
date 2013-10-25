# -*- coding: utf-8 -*-

import logging
import datetime

from google.appengine.ext import db
from google.appengine.ext.db import polymodel
from google.appengine.ext import blobstore

#-----------------------------------------------------------------------------

genders      = ["Male", "Female", "N/A"]
privacyTypes = ['Home', 'Work']
phoneTypes   = ["Landline", "Cellphone", "Internet", "Fax", "Other"]
wwwTypes     = ["Personal", "Company", "MySpace", "Facebook", "Twitter", "Google+"]

monthNames = {'00': 'Jan',
              '01': 'Feb',
              '02': 'Mar',
              '03': 'Apr',
              '04': 'May',
              '05': 'Jun',
              '06': 'Jul',
              '07': 'Aug',
              '08': 'Sep',
              '09': 'Oct',
              '10': 'Nov',
              '11': 'Dec'}

countries = {
    "AF": "Afghanistan",
    "AX": "Aland Islands",
    "AL": "Albania",
    "DZ": "Algeria",
    "AS": "American Samoa",
    "AD": "Andorra",
    "AO": "Angola",
    "AI": "Anguilla",
    "AQ": "Antarctica",
    "AG": "Antigua and Barbuda",
    "AR": "Argentina",
    "AM": "Armenia",
    "AW": "Aruba",
    "AU": "Australia",
    "AT": "Austria",
    "AZ": "Azerbaijan",
    "BS": "Bahamas",
    "BH": "Bahrain",
    "BD": "Bangladesh",
    "BB": "Barbados",
    "BY": "Belarus",
    "BE": "Belgium",
    "BZ": "Belize",
    "BJ": "Benin",
    "BM": "Bermuda",
    "BT": "Bhutan",
    "BO": "Bolivia",
    "BA": "Bosnia and Herzegovina",
    "BW": "Botswana",
    "BV": "Bouvet Island",
    "BR": "Brazil",
    "IO": "British Indian Ocean Territory",
    "BN": "Brunei Darussalam",
    "BG": "Bulgaria",
    "BF": "Burkina Faso",
    "BI": "Burundi",
    "KH": "Cambodia",
    "CM": "Cameroon",
    "CA": "Canada",
    "CV": "Cape Verde",
    "KY": "Cayman Islands",
    "CF": "Central African Republic",
    "TD": "Chad",
    "CL": "Chile",
    "CN": "China",
    "CX": "Christmas Island",
    "CC": "Cocos (Keeling) Islands",
    "CO": "Colombia",
    "KM": "Comoros",
    "CG": "Congo",
    "CD": "Congo, The Democratic Republic of The",
    "CK": "Cook Islands",
    "CR": "Costa Rica",
    "CI": "Cote D'ivoire",
    "HR": "Croatia",
    "CU": "Cuba",
    "CY": "Cyprus",
    "CZ": "Czech Republic",
    "DK": "Denmark",
    "DJ": "Djibouti",
    "DM": "Dominica",
    "DO": "Dominican Republic",
    "EC": "Ecuador",
    "EG": "Egypt",
    "SV": "El Salvador",
    "GQ": "Equatorial Guinea",
    "ER": "Eritrea",
    "EE": "Estonia",
    "ET": "Ethiopia",
    "FK": "Falkland Islands (Malvinas)",
    "FO": "Faroe Islands",
    "FJ": "Fiji",
    "FI": "Finland",
    "FR": "France",
    "GF": "French Guiana",
    "PF": "French Polynesia",
    "TF": "French Southern Territories",
    "GA": "Gabon",
    "GM": "Gambia",
    "GE": "Georgia",
    "DE": "Germany",
    "GH": "Ghana",
    "GI": "Gibraltar",
    "GR": "Greece",
    "GL": "Greenland",
    "GD": "Grenada",
    "GP": "Guadeloupe",
    "GU": "Guam",
    "GT": "Guatemala",
    "GG": "Guernsey",
    "GN": "Guinea",
    "GW": "Guinea-bissau",
    "GY": "Guyana",
    "HT": "Haiti",
    "HM": "Heard Island and Mcdonald Islands",
    "VA": "Holy See (Vatican City State)",
    "HN": "Honduras",
    "HK": "Hong Kong",
    "HU": "Hungary",
    "IS": "Iceland",
    "IN": "India",
    "ID": "Indonesia",
    "IR": "Iran, Islamic Republic of",
    "IQ": "Iraq",
    "IE": "Ireland",
    "IM": "Isle of Man",
    "IL": "Israel",
    "IT": "Italy",
    "JM": "Jamaica",
    "JP": "Japan",
    "JE": "Jersey",
    "JO": "Jordan",
    "KZ": "Kazakhstan",
    "KE": "Kenya",
    "KI": "Kiribati",
    "XK": "Kosovo",
    "KP": "Korea, Democratic People's Republic of",
    "KR": "Korea, Republic of",
    "KW": "Kuwait",
    "KG": "Kyrgyzstan",
    "LA": "Lao People's Democratic Republic",
    "LV": "Latvia",
    "LB": "Lebanon",
    "LS": "Lesotho",
    "LR": "Liberia",
    "LY": "Libyan Arab Jamahiriya",
    "LI": "Liechtenstein",
    "LT": "Lithuania",
    "LU": "Luxembourg",
    "MO": "Macao",
    "MK": "Macedonia, The Former Yugoslav Republic of",
    "MG": "Madagascar",
    "MW": "Malawi",
    "MY": "Malaysia",
    "MV": "Maldives",
    "ML": "Mali",
    "MT": "Malta",
    "MH": "Marshall Islands",
    "MQ": "Martinique",
    "MR": "Mauritania",
    "MU": "Mauritius",
    "YT": "Mayotte",
    "MX": "Mexico",
    "FM": "Micronesia, Federated States of",
    "MD": "Moldova, Republic of",
    "MC": "Monaco",
    "MN": "Mongolia",
    "ME": "Montenegro",
    "MS": "Montserrat",
    "MA": "Morocco",
    "MZ": "Mozambique",
    "MM": "Myanmar",
    "NA": "Namibia",
    "NR": "Nauru",
    "NP": "Nepal",
    "NL": "Netherlands",
    "AN": "Netherlands Antilles",
    "NC": "New Caledonia",
    "NZ": "New Zealand",
    "NI": "Nicaragua",
    "NE": "Niger",
    "NG": "Nigeria",
    "NU": "Niue",
    "NF": "Norfolk Island",
    "MP": "Northern Mariana Islands",
    "NO": "Norway",
    "OM": "Oman",
    "PK": "Pakistan",
    "PW": "Palau",
    "PS": "Palestinian Territory, Occupied",
    "PA": "Panama",
    "PG": "Papua New Guinea",
    "PY": "Paraguay",
    "PE": "Peru",
    "PH": "Philippines",
    "PN": "Pitcairn",
    "PL": "Poland",
    "PT": "Portugal",
    "PR": "Puerto Rico",
    "QA": "Qatar",
    "RE": "Reunion",
    "RO": "Romania",
    "RU": "Russian Federation",
    "RW": "Rwanda",
    "SH": "Saint Helena",
    "KN": "Saint Kitts and Nevis",
    "LC": "Saint Lucia",
    "PM": "Saint Pierre and Miquelon",
    "VC": "Saint Vincent and The Grenadines",
    "WS": "Samoa",
    "SM": "San Marino",
    "ST": "Sao Tome and Principe",
    "SA": "Saudi Arabia",
    "SN": "Senegal",
    "RS": "Serbia",
    "SC": "Seychelles",
    "SL": "Sierra Leone",
    "SG": "Singapore",
    "SK": "Slovakia",
    "SI": "Slovenia",
    "SB": "Solomon Islands",
    "SO": "Somalia",
    "ZA": "South Africa",
    "GS": "South Georgia and The South Sandwich Islands",
    "ES": "Spain",
    "LK": "Sri Lanka",
    "SD": "Sudan",
    "SR": "Suriname",
    "SJ": "Svalbard and Jan Mayen",
    "SZ": "Swaziland",
    "SE": "Sweden",
    "CH": "Switzerland",
    "SY": "Syrian Arab Republic",
    "TW": "Taiwan, Province of China",
    "TJ": "Tajikistan",
    "TZ": "Tanzania, United Republic of",
    "TH": "Thailand",
    "TL": "Timor-leste",
    "TG": "Togo",
    "TK": "Tokelau",
    "TO": "Tonga",
    "TT": "Trinidad and Tobago",
    "TN": "Tunisia",
    "TR": "Turkey",
    "TM": "Turkmenistan",
    "TC": "Turks and Caicos Islands",
    "TV": "Tuvalu",
    "UG": "Uganda",
    "UA": "Ukraine",
    "AE": "United Arab Emirates",
    "GB": "United Kingdom",
    "US": "United States",
    "UM": "United States Minor Outlying Islands",
    "UY": "Uruguay",
    "UZ": "Uzbekistan",
    "VU": "Vanuatu",
    "VE": "Venezuela",
    "VN": "Viet Nam",
    "VG": "Virgin Islands, British",
    "VI": "Virgin Islands, U.S.",
    "WF": "Wallis and Futuna",
    "EH": "Western Sahara",
    "YE": "Yemen",
    "ZM": "Zambia",
    "ZW": "Zimbabwe",
}

imTypes = {
    'Google': 'http://talk.google.com/',
    'Skype': 'http://www.skype.com/',
    'Gadu-gadu': 'http://gadu-gadu.pl/',
    'MSN': 'http://messenger.msn.com/',
    'Yahoo!': 'http://messenger.yahoo.com/',
}

availableLanguages = {
    'en': u'English',
    #'pl': u'Polski',
    #'de': u'Deutsch',
    #'jp': u'日本語',
}

#-----------------------------------------------------------------------------

class Group(db.Model):
    
    name = db.StringProperty()
    sync = db.BooleanProperty(default = True)

#-----------------------------------------------------------------------------

class UserSettings(db.Model):
    '''
    User settings other than those stored in the UserProfile.
    '''
    preferredLanguage = db.StringProperty(choices = availableLanguages.keys(),
                                          default = 'en')  # availableLanguages.keys()[0] is 'de', they seem to be sorted alphabetically   

    notifyEmails = db.BooleanProperty(default = True)
    notifyStopsUsingMyPrivateData = db.BooleanProperty(default = True)
    notifyAsksForPrivateData = db.BooleanProperty(default = True)
    notifyAllowsMePrivateData = db.BooleanProperty(default = True)
    notifyDisallowsMePrivateData = db.BooleanProperty(default = True)
    notifyRequestDecision = db.BooleanProperty(default = True)

    cardDAVenabled = db.BooleanProperty(default = False)
    #syncWithGoogle = db.BooleanProperty(default = False)

#-----------------------------------------------------------------------------

class UserAddress(db.Model):
    address = db.PostalAddressProperty()
    city = db.StringProperty(default = "")
    countryCode = db.StringProperty(default = "",
                                    choices = countries.keys() + [""])
    postalCode = db.StringProperty(default = "")
    privacyType = db.StringProperty(choices = privacyTypes)
    location = db.GeoPtProperty()
    creationTime = db.DateTimeProperty(auto_now_add = True)
    
    @property
    def itemValue(self):
        return u", ".join([self.address,
                           u" ".join([self.postalCode, self.city]),
                           countries[self.countryCode]])

#-----------------------------------------------------------------------------

class UserEmail(db.Model):
    itemValue = db.EmailProperty()
    privacyType = db.StringProperty(choices = privacyTypes)
    primary = db.BooleanProperty(default = False)
    creationTime = db.DateTimeProperty(auto_now_add = True)

#-----------------------------------------------------------------------------

class UserIM(db.Model):
    itemValue = db.IMProperty()
    privacyType = db.StringProperty(choices = privacyTypes)
    creationTime = db.DateTimeProperty(auto_now_add = True)

#-----------------------------------------------------------------------------

class UserPhoneNumber(db.Model):
    itemValue = db.PhoneNumberProperty(required = True)
    itemType = db.StringProperty(choices = phoneTypes)
    privacyType = db.StringProperty(choices = privacyTypes)
    creationTime = db.DateTimeProperty(auto_now_add = True)

#-----------------------------------------------------------------------------

class UserWebpage(db.Model):
    itemValue = db.LinkProperty()
    itemType = db.StringProperty(choices = wwwTypes)
    privacyType = db.StringProperty(choices = privacyTypes)
    creationTime = db.DateTimeProperty(auto_now_add = True)

#-----------------------------------------------------------------------------

class UserPhoto(db.Model):
    image = blobstore.BlobReferenceProperty()
    width = db.IntegerProperty()
    height = db.IntegerProperty()
    servingUrl = db.StringProperty()
    creationTime = db.DateTimeProperty(auto_now_add = True)

#-----------------------------------------------------------------------------

class UserNickname(db.Model):
    itemValue = db.StringProperty()
    creationTime = db.DateTimeProperty(auto_now_add = True)

#-----------------------------------------------------------------------------

class UserCompany(db.Model):
    companyName = db.StringProperty()
    positionName = db.StringProperty()
    creationTime = db.DateTimeProperty(auto_now_add = True)

#-----------------------------------------------------------------------------

class Persona(db.Model):
    
    name = db.StringProperty()
    public = db.BooleanProperty(default = False)
    
    canViewGivenNames = db.BooleanProperty(default = True)
    canViewFamilyNames = db.BooleanProperty(default = True)
    canViewPrefix = db.BooleanProperty(default = True)
    canViewSuffix = db.BooleanProperty(default = True)
    canViewRomanGivenNames = db.BooleanProperty(default = True)
    canViewRomanFamilyNames = db.BooleanProperty(default = True)

    canViewBirthday = db.BooleanProperty(default = False)
    canViewGender = db.BooleanProperty(default = False)

    vcard = db.TextProperty()   # vCard for CardDAV access; it's not a StringProperty
                                # because it might be longer than 500 characters
    vcardMTime = db.StringProperty() # modification time
    vcardMD5 = db.StringProperty()   # MD5 checksum of the vcard
    vcardNeedsUpdating = db.BooleanProperty(default = True)
    
    displayName = db.StringProperty()
    
    company = db.ReferenceProperty(UserCompany)
    nickname = db.ReferenceProperty(UserNickname)
    picture = db.ReferenceProperty(UserPhoto)

    @property
    def permitEmails(self):
        return PermitEmail.all().ancestor(self)
    
    @property
    def permitIMs(self):
        return PermitIM.all().ancestor(self)
    
    @property
    def permitWWWs(self):
        return PermitWebpage.all().ancestor(self)
    
    @property
    def permitPhones(self):
        return PermitPhoneNumber.all().ancestor(self)
    
    @property
    def permitAddresses(self):
        return PermitAddress.all().ancestor(self)

    @property
    def individualPermits(self):
        return IndividualPermit.all().ancestor(self)

#-----------------------------------------------------------------------------

class UserProfile(db.Model):

    created = db.DateTimeProperty(auto_now_add=True)
    updated = db.DateTimeProperty(auto_now=True)

    # Login data
    user = db.UserProperty()
    nativeLogin = db.BooleanProperty(default = False)
    username = db.StringProperty()
    email = db.StringProperty()
    passwordHash = db.StringProperty()
    passwordSalt = db.StringProperty()
    active = db.BooleanProperty(default = False)

    # Personal data
    namePrefix = db.StringProperty(default = u"")
    nameSuffix = db.StringProperty(default = u"")

    givenNames = db.StringProperty(default = u"")
    givenNamesRomanization = db.StringProperty(default = u"")
    
    familyNames = db.StringProperty(default = u"")
    familyNamesRomanization = db.StringProperty(default = u"")
    
    gender = db.StringProperty(choices = genders)
    birthDate = db.DateProperty(default = datetime.date(1900, 1, 1))  

    publicEnabled = db.BooleanProperty(default = True)

    # Shortcuts to non-removable personas
    defaultPersona = db.ReferenceProperty(Persona,
                                         collection_name = "userProfile1")
    publicPersona = db.ReferenceProperty(Persona,
                                        collection_name = "userProfile2")
    defaultGroup = db.ReferenceProperty(Group)
    
    userSettings = db.ReferenceProperty(UserSettings)
    
    @property
    def displayName(self):
        if self.publicEnabled:
            return self.publicPersona.displayName
        else:
            return u"Anonymous user " + unicode(self.key().id())
    
    @property
    def emails(self):
        return UserEmail.all().ancestor(self).order("-primary")

    @property
    def addresses(self):
        return UserAddress.all().ancestor(self)
    
    @property
    def ims(self):
        return UserIM.all().ancestor(self)
    
    @property
    def webpages(self):
        return UserWebpage.all().ancestor(self)
    
    @property
    def phones(self):
        return UserPhoneNumber.all().ancestor(self)
    
    @property
    def personas(self):
        return Persona.all().ancestor(self)

    @property
    def groups(self):
        return Group.all().ancestor(self)

    @property
    def photos(self):
        return UserPhoto.all().ancestor(self)

    @property
    def nicknames(self):
        return UserNickname.all().ancestor(self)

    @property
    def companies(self):
        return UserCompany.all().ancestor(self)

#-----------------------------------------------------------------------------

class Psinque(db.Model):
    
    fromUser = db.ReferenceProperty(UserProfile,
                                    collection_name = "outgoing")
    
    status = db.StringProperty(choices = ["pending", "established", "banned"])
    private = db.BooleanProperty(default = False)
    
    creationTime = db.DateTimeProperty(auto_now_add = True)
    
    persona = db.ReferenceProperty(Persona)
    
    @property
    def displayName(self):
        if not self.persona is None:
            return self.persona.displayName
        return self.fromUser.displayName
    
#-----------------------------------------------------------------------------

class Contact(db.Model):

    incoming = db.ReferenceProperty(Psinque,
                                    collection_name = "contact1")   
    outgoing = db.ReferenceProperty(Psinque,
                                    collection_name = "contact2")
    
    status = db.StringProperty(choices = ["public", "pending", "private"],
                               default = "public")

    friend = db.ReferenceProperty(UserProfile)
    friendsContact = db.SelfReferenceProperty()
    
    group = db.ReferenceProperty(Group)
    persona = db.ReferenceProperty(Persona)

    creationTime = db.DateTimeProperty(auto_now_add = True)

    @property
    def displayName(self):
        if self.status == "public":
            return self.friend.displayName
        if not self.incoming is None:
            return self.incoming.displayName
        #return self.friendsContact.persona.displayName

#-----------------------------------------------------------------------------

class Notification(db.Model):
    text = db.StringProperty()
    creationTime = db.DateTimeProperty(auto_now_add = True)


class Invitation(db.Model):
    email = db.EmailProperty()
    sentOn = db.DateTimeProperty(auto_now_add = True)
    acceptedOn = db.DateTimeProperty(auto_now = True)
    status = db.StringProperty(default = "pending")

#-----------------------------------------------------------------------------

class IndividualPermit(polymodel.PolyModel):
    canView = db.BooleanProperty(default = False)

class PermitEmail(IndividualPermit):
    userEmail = db.ReferenceProperty(UserEmail,
                                     collection_name = "individualPermits")


class PermitIM(IndividualPermit):
    userIM = db.ReferenceProperty(UserIM,
                                  collection_name = "individualPermits")


class PermitWebpage(IndividualPermit):
    userWebpage = db.ReferenceProperty(UserWebpage,
                                       collection_name = "individualPermits")


class PermitPhoneNumber(IndividualPermit):
    userPhoneNumber = db.ReferenceProperty(UserPhoneNumber,
                                           collection_name = "individualPermits")


class PermitAddress(IndividualPermit):
    userAddress = db.ReferenceProperty(UserAddress,
                                       collection_name = "individualPermits")


#-----------------------------------------------------------------------------

class CardDAVLogin(db.Model):
    name = db.StringProperty()
    generatedUsername = db.StringProperty()
    generatedPasswordHash = db.StringProperty()
    salt = db.StringProperty()
    lastUsed = db.DateTimeProperty(auto_now=True)

#-----------------------------------------------------------------------------
