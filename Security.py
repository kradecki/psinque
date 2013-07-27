
def psinqueMD5(self, data, salt):
    return md5(salt + ":" + data).hexdigest()
