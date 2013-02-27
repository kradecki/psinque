
import os.path
import logging

try:
    from cStringIO import StringIO
except ImportError:
    from StringIO import StringIO

from wsgidav.dav_provider import DAVProvider, _DAVResource

from users.UserManagement import generateVCard, friendList, groupList, CardDAVUser

carddavRoot = "/carddav"

class CardDAVResource(_DAVResource):

    def __init__(self, path, environ):
        path = os.path.normpath(path)
        groupName = os.path.dirname(path)
        if os.path.dirname(groupName) != carddavRoot:
            raise ValueError("Unsupported path: %r" % path)
        self.groupName = os.path.basename(groupName)
        fileName = os.path.basename(path)
        isCollection = (fileName == u"")
        if not isCollection:
            fileName = os.path.splitext(fileName)
            if fileName[1] != u".vcf":
                raise ValueError("Unsupported extension: %r" % fileName[1])
            self.friendID = fileName[0]
        
        self.user  = cardDAVUser(environ["wsgidav.username"])
        self.vCard = None  # we're lazy at generating the vCard
        
        logging.debug("CardDAVResource(%r): %r" % (path, isCollection))
        super(CardDAVResource, self).__init__(path, isCollection, environ)
        
    def getContentLength(self):
        if self.isCollection:
            return None
        if self.vCard is None:
            self.vCard = generateVCard(self.user, self.friendID)
        return len(self.vCard)
    
    def getContentType(self):
        if self.isCollection:
            return "httpd/unix-directory"  #TODO: Check MIME for WebDAV folders
        return "text/vcard"
    
    def getMemberNames(self):
        assert self.isCollection
        if self.path == carddavRoot:
            memberNames = groupList(self.user)
        memberNames = friendList(self.user, self.groupName)
        return [ os.path.basename(self.path) + "/" + memberName for memberName in memberNames ]
    
    def getContent(self):
        assert not self.isCollection
        if self.vCard is None:
            self.vCard = generateVCard(self.user, self.friendID)
        return StringIO(self.vCard)

class CardDAVProvider(DAVProvider):
    
    def getResourceInst(self, path, environ):
        self._count_getResourceInst += 1
        try:
            res = CardDAVResource(path, environ)
        except:
            logging.exception("getResourceInst(%r) failed" % path)
            res = None
        logging.debug("getResourceInst(%r): %s" % (path, res))
        return res
