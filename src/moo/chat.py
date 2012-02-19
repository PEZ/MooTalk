#!/usr/bin/env python
# -*- coding: latin-1 -*-

from google.appengine.ext import db
from  google.appengine.api import xmpp
from google.appengine.api import users
import os
from moo.user import User

class Chat(db.Model):
    title = db.StringProperty(required=True)
    participants = db.StringListProperty()
    non_listeners = db.StringListProperty()
    taglines = db.StringListProperty()

    @classmethod
    def create(cls, title):
        if title not in [chat.title for chat in cls.all()]:
            chat = cls(title=title)
            chat.put()
            return chat
        else:
            return None
    
    @property
    def jid(self):
        return "%s@%s.appspotchat.com" % (self.title, os.environ['APPLICATION_ID'])
    
    @property
    def listeners(self):
        return list(set(u for u in self.users if u.address not in self.non_listeners))

    @property
    def users(self):
        return [User.user(p) for p in self.participants if User.user(p)]

    @property
    def non_users(self):         
        return [u for u in User.all() if not self.title in [c.title for c in u.chats]]
        
    @classmethod
    def chat_user(cls, chat, participant):
        return chat.participant_user(participant)
    
    def clean_chat_from_non_users(self):
        import logging
        for email in self.participants:
            try: 
                User.all().filter('address =', email).fetch(1)[0]
            except IndexError:
                logging.error("Cleaning away non user %s from chat %s" % (email, self.title))
                self.remove_participant(email)

    def _update_taglinesTx(self, taglines):
        self.taglines = taglines
        self.put()

    @property
    def taglines_as_text(self):
        return "\n".join(self.taglines)

    def update_taglines(self, taglines_text):
        """
        Takes a chunk of text, splits it up on newlines, removes empty lines and updates the list of taglines
        """
        taglines = [tagline.strip() for tagline in taglines_text.split('\n') if tagline.strip() != '']
        if taglines:
            db.run_in_transaction(self._update_taglinesTx, taglines)

    def _add_participantTx(self, address):
        if address not in self.participants:
            self.participants.append(address)
            self.put()

    def add_participant(self, address):
        """
        Adds a user to a chat and also sends an invitation to the user to authorize the channel.
        """
        if address in [u.address for u in User.all()]:
            db.run_in_transaction(self._add_participantTx, address)
            xmpp.send_invite(address, self.jid)
    
    def _remove_participantTx(self, address):
        if address in self.participants:
            self.participants.remove(address)
            self.put()
    
    def remove_participant(self, address):
        remove_msg = "You have been removed from this channel by %s." % users.get_current_user().nickname()
        db.run_in_transaction(self._remove_participantTx, address)
        xmpp.send_message(address, remove_msg, self.jid, xmpp.MESSAGE_TYPE_HEADLINE)
    
    def add_listener(self, address):
        if address in self.non_listeners:
            self.non_listeners.remove(address)
            self.put()
    
    def remove_listener(self, address):
        if address not in self.non_listeners and address in [u.address for u in User.all()]:
            self.non_listeners.append(address)
            self.put()

    @classmethod
    def chat_from_title(cls, title):
        chat = cls.all()
        chat.filter("title =", title)
        return chat.get()