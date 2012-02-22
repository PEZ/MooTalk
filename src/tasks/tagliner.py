#!/usr/bin/env python
# -*- coding: latin-1 -*-
'''
Created on Feb 19, 2012

@author: pez
'''

from google.appengine.api import xmpp
from moo.chat import Chat
import moo.messages as messages
import wsgiref.handlers
from google.appengine.ext import webapp

def get_chats_with_taglines():
    return [chat for chat in Chat.all() if chat.taglines != []]

def get_random_tagline(chat):
    from random import choice
    return choice(chat.taglines)

class Tagliner(webapp.RequestHandler):
    message_template = messages.TAGLINE_MESSAGE

    def get(self):
        chats = get_chats_with_taglines()
        for chat in chats:
            tagline = get_random_tagline(chat)
            addresses = [u.address for u in chat.listeners if xmpp.get_presence(u.address, chat.jid)]
            xmpp.send_message(addresses, messages.TAGLINE_MESSAGE % tagline, chat.jid)

def main():
    app = webapp.WSGIApplication([
        ('/tasks/tagliner', Tagliner)], debug=True)
    wsgiref.handlers.CGIHandler().run(app)

if __name__ == '__main__':
    main()