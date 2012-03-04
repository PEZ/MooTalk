import logging
from google.appengine.ext.webapp.mail_handlers import InboundMailHandler
from google.appengine.api import xmpp
from moo.chat import Chat
from moo.user import User
from moo.user import user_in_chat
import moo.messages as messages
from email.utils import parseaddr
from email.header import decode_header

def get_header(header_text, default="iso-8859-1"):
    """Decode the specified header"""

    headers = decode_header(header_text)
    try:
        header_sections = [unicode(text, charset or default)
                           for text, charset in headers]
        return u"".join(header_sections)
    except:
        return header_text

def get_sender_address(message):
    return parseaddr(message.sender)[1].lower()

def get_to_address(message):
    return parseaddr(message.to)[1].lower()

def get_chat(address):
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
            recipients = [r.address for r in self.chat.listeners]
            if len(recipients) > 0:
                message = get_header(email_message.subject)
                message = message_template % (self.sender.nickname, message)
                logging.info("Email handler sending message. Chat-jid: %s, message: %s" % (self.chat.jid, message))
                xmpp.send_message(recipients, message, self.chat.jid)
