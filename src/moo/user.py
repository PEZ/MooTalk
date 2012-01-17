from google.appengine.ext import db
from gravatar import gravatar

class User(db.Model):
    nickname = db.StringProperty()
    address = db.StringProperty(required=True)
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
    def murder(cls, murder_key):
        import logging
        
        user = User.get(murder_key)
        logging.info("REMOVING User %s" % user.nickname)
        for chat in user.chats:
            logging.info("REMOVING %s from chat %s" % (user.nickname, chat.title))
            chat.remove_participant(user.address)
            chat.clean_chat_from_non_users()
        
        user.delete()
    
    @property
    def chats(self):     
        from moo.chat import Chat
        return db.get(Chat.all(keys_only=True).filter("participants =", self.address))        
            