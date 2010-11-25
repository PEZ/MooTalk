#!/usr/bin/env python
# -*- coding: utf-8 -*-

from test import ModelTestCase
from moo.chat import Chat
from moo.user import User

class TestChat(ModelTestCase):
    '''Tests for Moo Chat Models'''
    chat = None
    user1 = None
    user2 = None
    user3 = None
    
    def setUp(self):
        super(TestChat, self).setUp()
        self.chat = Chat.create(title='chat 1')
        self.user1 = User.create('u1', 'u1@foo')
        self.user2 = User.create('u2', 'u2@foo')
        self.user3 = User.create('u3', 'u3@foo')
        self.chat.add_participant(self.user1.address)
        self.chat.add_participant(self.user2.address)
        self.chat.add_participant(self.user3.address)
        self.chat.put()
        
    def test_chats_default_listeners(self):
        '''A chat's listeners list is the same as the participants list by default'''
        self.assertEqual(self.chat.participants, [u.address for u in self.chat.listeners])

    def test_chats_add_remove_listeners(self):
        '''Adding and removing listeners'''
        self.chat.add_listener(self.user1)
        self.assertEqual(self.chat.participants, [u.address for u in self.chat.listeners])
        self.chat.remove_listener(self.user1.address)
        self.assertEqual(set([u.key() for u in self.user2, self.user3]), set(u.key() for u in self.chat.listeners))