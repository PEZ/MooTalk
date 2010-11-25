import hashlib
import urllib

def gravatar(email, size=80, rating='g', default_image=''):
        gravatar_url = "http://www.gravatar.com/avatar/"
        gravatar_url += hashlib.md5(email).hexdigest()
        gravatar_url += '.jpg?' + urllib.urlencode({'s':str(size),
                'r':rating,
                'd':default_image})
        return gravatar_url