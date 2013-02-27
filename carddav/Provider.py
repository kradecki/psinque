
import os.path
import logging

from string import replace

try:
    from cStringIO import StringIO
except ImportError:
    from StringIO import StringIO

from wsgidav import util
from wsgidav.dav_provider import DAVProvider, _DAVResource

from users import UserManagement

carddavRoot = "/"

class CardDAVResource(_DAVResource):

    def __init__(self, path, environ):
        logging.error("CardDAVResource(" + path + ")")
        path = os.path.normpath(path)
        path = replace(path, "//", "/")
        if path == "/":
            isCollection = True
        else:
            self.groupName = os.path.dirname(path)
            fileName = os.path.basename(path)
            if self.groupName == "/" and fileName != "":
                isCollection = True
                fileName = self.groupName
                self.groupName = ""
            else:
                fileName = os.path.splitext(fileName)
                if fileName[1] != u".vcf":
                    raise ValueError("Unsupported extension: %r" % fileName[1])
                self.friendID = fileName[0]           
                self.vCard = None  # we're lazy at generating the vCard
        
        self.user = UserManagement.cardDAVUser(environ["wsgidav.username"])
        
        logging.debug("CardDAVResource(%r): %r" % (path, isCollection))
        super(CardDAVResource, self).__init__(path, isCollection, environ)
        
    def getContentLength(self):
        logging.error("getContentLength")
        if self.isCollection:
            return None
        if self.vCard is None:
            self.vCard = generateVCard(self.user, self.friendID)
        return len(self.vCard)
    
    def getContentType(self):
        logging.error("getContentType")
        if self.isCollection:
            return "httpd/unix-directory"  #TODO: Check MIME for WebDAV folders
        return "text/vcard"
    
    def getMemberNames(self):
        logging.error("getMemberNames")
        assert self.isCollection
        if self.path == carddavRoot:
            memberNames = UserManagement.groupList(self.user)
        else:
            memberNames = UserManagement.friendList(self.user, self.groupName)
        logging.error(memberNames)
        return [ os.path.basename(self.path) + "/" + memberName for memberName in memberNames ]
    
    def getContent(self):
        logging.error("getContent")
        assert not self.isCollection
        if self.vCard is None:
            self.vCard = generateVCard(self.user, self.friendID)
        return StringIO(self.vCard)

    def getMember(self, name):
        """
        Return child resource with a given name (None, if not found).
        """
        logging.error("getMember(" +name+ ")")
        assert self.isCollection
        return self.provider.getResourceInst(util.joinUri(self.path, name), 
                                             self.environ)

    def getMemberList(self):
        """
        Return a list of direct members (_DAVResource or derived objects).
        """
        logging.error("getMemberList")
        if not self.isCollection:
            raise NotImplementedError()
        memberList = [] 
        for name in self.getMemberNames():
            member = self.getMember(name) 
            memberList.append(member)
        return memberList

class CardDAVProvider(DAVProvider):
    
    def getResourceInst(self, path, environ):
        logging.error("getResourceInst(" +path+ ")")
        self._count_getResourceInst += 1
        try:
            res = CardDAVResource(path, environ)
        except:
            logging.exception("getResourceInst(%r) failed" % path)
            res = None
        logging.debug("getResourceInst(%r): %s" % (path, res))
        return res
