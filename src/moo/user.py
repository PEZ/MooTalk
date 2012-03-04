from google.appengine.ext import db
from gravatar import gravatar
from moo.utils import textlines_to_list

def user_in_chat(user, chat):
    '''This user has access to this chat?'''
    return chat != None and user != None and user.address in chat.participants 

class User(db.Model):
    nickname = db.StringProperty(required=True)
    address = db.StringProperty(required=True)
    _email_addresses = db.StringListProperty()
    avatar = db.LinkProperty()

    @classmethod
    def create(cls, nickname, address):
        address = address.strip()
        if address not in [u.address for u in User.all()]:
            user = cls(nickname=nickname, address=address)
            user.avatar = db.Link(gravatar(address, size=48))
            user.put()
            return user
        else:
            return None
    
    @classmethod
    def user(cls, address):
        user = cls.all()
        user.filter("address =", address)
        return user.get()
    
    @classmethod
    def user_from_nick(cls, nick):
        user = cls.all()
        user.filter("nickname =", nick)
        return user.get()
    
    @classmethod
    def user_from_email_address(cls, address):
        user = cls.all()
        user.filter("_email_addresses =", address)
        return user.get()
    
    @classmethod
    def user_from_any_address(cls, address):
        user = cls.user(address)
        if user is not None:
            return user
        else:
            user = cls.all()
            user.filter("_email_addresses =", address)
            return user.get()
    
    @classmethod
    def murder(cls, murder_key):
        import logging
        
        user = User.get(murder_key)
        logging.info("REMOVING User %s" % user.nickname)
        for chat in user.chats:
            logging.info("REMOVING %s from chat %s" % (user.nickname, chat.title))
            chat.remove_participant(user.address)
            chat.clean_chat_from_non_users()
        
        user.delete()

    def email_addresses_get(self):
        return self._email_addresses
    
    def email_addresses_set(self, addresses):
        if type(addresses) in (str, type(u'')):
            self._email_addresses = textlines_to_list(addresses)
        else:
            self._email_addresses = addresses
        self.put()
    
    email_addresses = property(email_addresses_get, email_addresses_set)

    @property
    def email_addresses_as_text(self):
        return '\n'.join(self._email_addresses)

    @property
    def chats(self):
        from moo.chat import Chat
        return db.get(Chat.all(keys_only=True).filter("participants =", self.address))        
            