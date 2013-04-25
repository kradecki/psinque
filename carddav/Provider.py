
import os.path
import logging

from string import replace

try:
    from cStringIO import StringIO
except ImportError:
    from StringIO import StringIO

from wsgidav.dav_error import DAVError, HTTP_NOT_FOUND
from wsgidav.dav_provider import DAVProvider, _DAVResource
from wsgidav import util

from lxml import etree
from datetime import datetime
import md5

from users import UserManagement

class CardDAVResource(_DAVResource):

    def __init__(self, path, environ):
        path = os.path.normpath(path)
        path = replace(path, "//", "/")
        assert path=="" or path.startswith("/")
        #logging.info("CardDAVResource(" + path + ")")

        self.provider = environ["wsgidav.provider"]
        self.path = path
        self.environ = environ
        self.user = UserManagement.cardDAVUser(environ["wsgidav.username"])

        if (path == "/") or (path == ""):  # this is the main folder
            self.isCollection = True
            self.name = "Psinque"
        else:
            self.groupName = os.path.dirname(path)
            fileName = os.path.basename(path)
            #logging.info("groupName = " + self.groupName)
            #logging.info("fileName = " + fileName)
            if self.groupName == "/":
                self.groupName = fileName
                fileName = ""
            if fileName != "":
                fileName = os.path.splitext(fileName)
                self.isCollection = False
                #logging.info("- resourcetype: non-collection")
                if fileName[1] != u".vcf":
                    raise ValueError("Unsupported extension: %r" % fileName[1])
                self.friendID = fileName[0]           
                self.name = "Forest Gump"
                self.vCard = None  # we're lazy at generating the vCard
            else:
                self.isCollection = True
                #logging.info("- resourcetype: collection")
                self.name = self.groupName
    
    def generateVCard(self):
        if not self.isCollection and self.vCard is None:
            self.vCard = UserManagement.generateVCard(self.user, self.friendID)
            self.vcard_mtime = str(datetime.date(datetime.now())) + "-" + str(datetime.time(datetime.now()))
    
    def getContentLength(self):
        #logging.info("getContentLength()")
        if self.isCollection:
            return None
        self.generateVCard()
        return len(self.vCard)
    
    def getContentType(self):
        #logging.info("getContentType()")
        if self.isCollection:
            return "httpd/unix-directory"  #TODO: Check MIME for WebDAV folders
        return "text/vcard"
    
    def getEtag(self):
        '''
        ETags are essential for caching.
        '''
        #logging.info("getEtag()")
        if self.isCollection:
            return '"' + md5.new(self.path).hexdigest() +'"'
        self.generateVCard()
        return md5.new(self.path).hexdigest() + '-' + str(self.vcard_mtime)
    
    def getMemberNames(self):
        #logging.info("getMemberNames(" + self.path +")")
        assert self.isCollection
        if self.path == "/":
            memberNames = UserManagement.groupList(self.user)
        else:
            memberNames = UserManagement.friendList(self.user, self.groupName)
        #logging.info(memberNames)
        #return [ os.path.basename(self.path) + "/" + memberName for memberName in memberNames ]
        return memberNames
    
    def getContent(self):
        logging.info("getContent()")
        assert not self.isCollection
        self.generateVCard()
        return StringIO(self.vCard)
    
    #def getCreationDate(self):
        #logging.info("getCreationDate()")
        #self.generateVCard()
        #return str(self.vcard_mtime)
        
    #def getLastModified(self):
        #logging.info("getLastModified()")
        #self.generateVCard()
        #return str(self.vcard_mtime)

    def getMember(self, name):
        """
        Return child resource with a given name (None, if not found).
        """
        #logging.info("getMember(" +name+ ")")
        assert self.isCollection
        return self.provider.getResourceInst(util.joinUri(self.path, name), 
                                             self.environ)

    def getMemberList(self):
        """
        Returns a list of direct members (_DAVResource or derived objects).
        """
        #logging.info("getMemberList()")
        if not self.isCollection:
            raise NotImplementedError()
        memberList = [] 
        for name in self.getMemberNames():
            member = self.getMember(name) 
            memberList.append(member)
        return memberList
    
    def getPropertyNames(self, isAllProp):
        
        #logging.info("getPropertyNames(" + isAllProp + ")")
        
        # The basic WebDAV properties:
        propNameList = super(CardDAVResource, self).getPropertyNames(self, isAllProp)
        
        # Plus all the CardDAV-related stuff
        propNameList.append("{DAV:}current-user-principal")
        propNameList.append("{DAV:}principal-URL")
        propNameList.append("{DAV:}principal-collection-set")
        propNameList.append("{urn:ietf:params:xml:ns:carddav}addressbook-home-set")
        propNameList.append("{DAV:}supported-report-set")   # which REPORT requests are supported by our server
        propNameList.append("{urn:ietf:params:xml:ns:carddav}address-data")   # the actual content of the vCard
        propNameList.append("{DAV:}owner")
        
        return propNameList


    def getPropertyValue(self, propname):
        
        #logging.info(self.path + ":getPropertyValue(" + propname + ")")
        
        if (propname == "{urn:ietf:params:xml:ns:carddav}addressbook-home-set" or
           propname == "{DAV:}current-user-principal" or
           propname == "{DAV:}principal-URL" or
           propname == "{DAV:}principal-collection-set"):
             propertyEL = etree.Element(propname)
             hrefEL = etree.SubElement(propertyEL, "{DAV:}href")
             hrefEL.text = "/carddav/"
             return propertyEL
        
        if propname == "{DAV:}owner":
            return "/carddav/"
        
        if propname == "{DAV:}supported-report-set":
            propertyEL = etree.Element(propname)
            #TODO: The following is not true, check which ones can be removed and add {urn:ietf:params:xml:ns:carddav}addressbook-multiget instead
            for reportName in ["principal-property-search", "sync-collectionexpand-property", "principal-search-property-set"]:
                newEl = etree.SubElement(propertyEL, "{DAV:}supported-report")
                newReportName = etree.SubElement(newEl, "{DAV:}report")
                newReportName.text = reportName
            return propertyEL
         
        if propname == "{urn:ietf:params:xml:ns:carddav}address-data":
            self.generateVCard()
            return self.vCard
         
        if propname == "{DAV:}current-user-privilege-set":
            propertyEL = etree.Element(propname)
            hrefEL = etree.SubElement(propertyEL, "{DAV:}privilege")
            for privilege in ["{DAV:}all", "{DAV:}read", "{DAV:}write", "{DAV:}write-properties", "{DAV:}write-content"]:
                etree.SubElement(hrefEL, privilege)
            return propertyEL
         
        if propname == "{DAV:}resourcetype":
            if self.isCollection:
                resourcetypeEL = etree.Element(propname)
                etree.SubElement(resourcetypeEL, "{DAV:}collection")
                if self.path == "/":
                    etree.SubElement(resourcetypeEL, "{DAV:}principal")
                else:
                    etree.SubElement(resourcetypeEL, "{urn:ietf:params:xml:ns:carddav}addressbook")
                return resourcetypeEL            
            return ""
        
        # In all other cases, use standard WebDAV
        return super(CardDAVResource, self).getPropertyValue(propname)


    def supportRanges(self):
        """Return True, if this non-resource supports Range on GET requests.

        This method MUST be implemented by non-collections only.
        """
        return False


class CardDAVProvider(DAVProvider):
    
    def getResourceInst(self, path, environ):
        #logging.info("getResourceInst(" +path+ ")")
        self._count_getResourceInst += 1
        try:
            res = CardDAVResource(path, environ)
        except:
            logging.exception("getResourceInst(%r) failed" % path)
            res = None
        return res


class WellKnownResource(_DAVResource):

    def __init__(self, path, environ):
        path = os.path.normpath(path)
        path = replace(path, "//", "/")
        #logging.info("WellKnownResource(" + path + ")")
        if path != "/carddav":
            raise DAVError(HTTP_NOT_FOUND)
        super(WellKnownResource, self).__init__(path, False, environ)
       
    def getPropertyNames(self, isAllProp):
        #logging.info("getPropertyNames(" + isAllProp + ")")
        propNameList = super(WellKnownResource, self).getPropertyNames(self, isAllProp)
        propNameList.append("{DAV:}current-user-principal")
        propNameList.append("{DAV:}principal-URL")
        propNameList.append("{urn:ietf:params:xml:ns:carddav}addressbook-home-set")
        return propNameList

    def getPropertyValue(self, propname):
        #logging.info("getPropertyValue(" + propname + ")")
        if (propname == "{urn:ietf:params:xml:ns:carddav}addressbook-home-set" or
           propname == "{DAV:}current-user-principal" or
           propname == "{DAV:}principal-URL"):
             propertyEL = etree.Element(propname)
             hrefEL = etree.SubElement(propertyEL, "{DAV:}href")
             hrefEL.text = "/carddav/"
             return propertyEL
        return super(WellKnownResource, self).getPropertyValue(propname)


class WellKnownProvider(DAVProvider):
    
    def getResourceInst(self, path, environ):
        #logging.info("getResourceInst(" +path+ ")")
        self._count_getResourceInst += 1
        try:
            res = WellKnownResource(path, environ)
        except:
            logging.exception("getResourceInst(%r) failed" % path)
            res = None
        return res
