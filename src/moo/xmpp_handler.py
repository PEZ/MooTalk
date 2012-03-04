import logging
from google.appengine.api import xmpp
from google.appengine.ext.webapp import xmpp_handlers
from moo.chat import Chat
from moo.user import User
from moo.user import user_in_chat
import moo.messages as messages

def get_chat(message):
    to = message.to.strip()
    chat_title = to.split('\40')[0]
    if chat_title == to:
        chat_title = to.split('@')[0]
    return Chat.all().filter('title =', chat_title).get()

def get_chat_and_user(message):
    sender_address = message.sender.split('/')[0].lower()
    return get_chat(message), User.user(sender_address)

def user_listing(users):
    return "\n".join(["""  %s %s""" % (u.nickname, u.address) for u in users])

class XmppHandler(xmpp_handlers.CommandHandler):
    chat = None
    sender = None

    def set_chat_and_user(self, message):
        sender_address = message.sender.split('/')[0].lower()
        (self.chat, self.sender) = (get_chat(message), User.user(sender_address))
        if user_in_chat(self.sender, self.chat):
            return True
        else:
            message.reply(messages.NO_ACCESS)
            logging.info("Denied access for address %s to chat %s" % (sender_address, self.chat))
            return False

    def unhandled_command(self, message=None):
        if self.set_chat_and_user(message):
            message.reply(messages.HELP_MSG % self.chat.email_address)

    def _send_text(self, text, to, shout=False):
        message_template = messages.MESSAGE
        recipients = [r for r in self.chat.participants if r != self.sender.address]
        if not shout:
            for r in self.chat.non_listeners:
                if r in recipients:
                    recipients.remove(r)
        else:
            message_template = messages.SHOUT_MESSAGE
        if len(recipients) > 0:
            xmpp.send_message(recipients, message_template % (self.sender.nickname, text), to)
        
    def text_message(self, message=None):
        if self.set_chat_and_user(message):
            self._send_text(message.body, message.to, shout=False)

    def shout_command(self, message=None):
        if self.set_chat_and_user(message):
            self._send_text(message.arg, message.to, shout=True)
    
    def mute_command(self, message=None):
        if self.set_chat_and_user(message):
            self.chat.remove_listener(self.sender.address)
            message.reply(messages.MUTE_MESSAGE)

    def unmute_command(self, message=None):
        if self.set_chat_and_user(message):
            self.chat.add_listener(self.sender.address)
            message.reply(messages.UNMUTE_MESSAGE)

    def pm_command(self, message=None):
        if self.set_chat_and_user(message):
            arg = message.arg.strip()
            space = arg.find(' ')
            to = arg[:space]
            msg = arg[space+1:]
            user = User.user(to)
            if user == None:
                user = User.user_from_nick(to)
            if user != None:
                xmpp.send_message(user.address, messages.PRIVATE_MESSAGE % (self.sender.nickname, msg), message.to)
            else:
                logging.info("Failed PM from '%s' to '%s' in channel '%s'." % (self.sender.nickname, to, self.chat))
                message.reply(messages.SYSTEM_MESSAGE % "No such user")
    
    msg_command = pm_command

    def me_command(self, message=None):
        if self.set_chat_and_user(message):
            msg = message.arg.strip()
            recipients = [r for r in self.chat.participants if r != self.sender.address]
            if len(recipients) > 0:
                xmpp.send_message(recipients, messages.ME_MESSAGE % (self.sender.nickname, msg), message.to)

    def who_command(self, message=None):
        if self.set_chat_and_user(message):
            arg = message.arg.strip()
            if arg in ["", "am i", "online"]:
                if arg == "am i":
                    message.reply(messages.SYSTEM_MESSAGE % ("You are " + user_listing([self.sender])))
                else:
                    who = "\nOnline:\n"
                    listeners = [u for u in self.chat.listeners if xmpp.get_presence(u.address, message.to)]
                    who += user_listing(listeners)
                    if arg != "online":
                        offlines = [u for u in self.chat.users if not xmpp.get_presence(u.address, message.to)]
                        who += "\n\nOffline:\n"
                        who += user_listing(offlines)
                    who += "\n\nOnline, but has muted this chat:\n"
                    non_listeners = [User.user(address) for address in self.chat.non_listeners if xmpp.get_presence(address, message.to)]
                    who += user_listing(non_listeners)
                    message.reply(messages.SYSTEM_MESSAGE % who)
            else:
                message.reply(messages.HELP_MSG)