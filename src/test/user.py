#!/usr/bin/env python
# -*- coding: utf-8 -*-

from test import ModelTestCase
from moo.chat import Chat
from moo.user import User

class TestUser(ModelTestCase):
    '''Tests for Moo User Models'''

    def test_chats(self):
        '''A users chats property is a list of all chats the user is listed as a participant'''
        user = User(nickname='Foo', address='foo@bar.com')
        user.put()
        chat1 = Chat.create(title='1')
        chat2 = Chat.create(title='2')
        chat3 = Chat.create(title='3') #@UnusedVariable
        chat1.add_participant(user.address)
        chat2.add_participant(user.address)
        self.assertEqual(set(c.key() for c in [chat1, chat2]), set(c.key() for c in user.chats))