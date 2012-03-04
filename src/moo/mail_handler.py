import logging
from google.appengine.ext.webapp.mail_handlers import InboundMailHandler
from google.appengine.api import xmpp
from moo.chat import Chat
from moo.user import User
from moo.user import user_in_chat
import moo.messages as messages
from email.utils import parseaddr

def get_sender_address(message):
    return parseaddr(message.sender)[1].lower()

def get_to_address(message):
    return parseaddr(message.to)[1].lower()

def get_chat(address):
    logging.info("address: %s", address)
    chat_title = address.split('@')[0]
    return Chat.all().filter('title =', chat_title).get()

def get_chat_and_user(message):
    to_address = get_to_address(message)
    sender_address = get_sender_address(message)
    return get_chat(to_address), User.user_from_any_address(sender_address)

class MailHandler(InboundMailHandler):
    chat = None
    sender = None

    def set_chat_and_user(self, message):
        self.chat, self.sender = get_chat_and_user(message)
        if user_in_chat(self.sender, self.chat):
            return True
        else:
            logging.info("Denied e-mail access for sender %s to chat %s" % (get_sender_address(message), self.chat))
            return False

    def receive(self, email_message):
        if self.set_chat_and_user(email_message):
            message_template = messages.EMAIL_MESSAGE
            recipients = [r.address for r in self.chat.listeners if r.key() != self.sender.key()]
            if len(recipients) > 0:
                message = message_template % (self.sender.nickname, email_message.subject)
                logging.info("Email handler sending message. Chat-jid: %s, message: %s" % (self.chat.jid, message))
                xmpp.send_message(recipients, message, self.chat.jid)
