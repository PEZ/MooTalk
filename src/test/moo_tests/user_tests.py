#!/usr/bin/env python
# -*- coding: utf-8 -*-

from test import ModelTestCase
from moo.chat import Chat
from moo.user import User

class UserTestCaseBase(ModelTestCase):
    user = None

    def setUp(self):
        ModelTestCase.setUp(self)
        self.user = User.create('Foo', 'foo@bar.com')
    
    def tearDown(self):
        ModelTestCase.tearDown(self)
        self.user.delete()
        self.user = None

class TestUserGeneral(UserTestCaseBase):
    
    def test_user_from_address(self):
        '''Get a user using the registered XMPP address'''
        self.assertEqual(self.user.key(), User.user(self.user.address).key())

    def test_user_from_nick(self):
        '''Retrieve a user using the nick name'''
        self.assertEqual(self.user.key(), User.user_from_nick(self.user.nickname).key())

class TestUserChats(UserTestCaseBase):

    def test_chats(self):
        '''A users chats property is a list of all chats the user is listed as a participant'''
        chat1 = Chat.create(title='1')
        chat2 = Chat.create(title='2')
        chat3 = Chat.create(title='3') #@UnusedVariable
        chat1.add_participant(self.user.address)
        chat2.add_participant(self.user.address)
        self.assertEqual(set(c.key() for c in [chat1, chat2]), set(c.key() for c in self.user.chats))

class TestUserEmailAddresses(UserTestCaseBase):
    user = None
    address1, address2 = None, None

    def setUp(self):
        UserTestCaseBase.setUp(self)
        self.address1, self.address2 = 'a1@foo.bar', 'a2@foo.bar'
        self.user.email_addresses = '''%s
        %s''' % (self.address1, self.address2)

    def test_default_email_addresses(self):
        '''Empty list of addresses when addresses are not assigned'''
        user = User.create('A', 'B')
        self.assertEqual([], user.email_addresses)

    def test_clear_email_addresses(self):
        '''Updating with no addresses should clear the list of addresses'''
        self.user.email_addresses = ''
        self.assertEqual(self.user.email_addresses, [])

    def test_email_addresses_as_text(self):
        '''The email_addresses_as_text property returns all taglines as a string separating taglines using newline'''
        self.assertEqual('%s\n%s' % (self.address1, self.address2), self.user.email_addresses_as_text)

    def test_user_from_email_address(self):
        '''Retrieve a user from one of her e-mail addresses'''
        self.assertEqual(User.user_from_email_address(self.address2).key(), self.user.key())

    def test_user_from_email_address_not_found(self):
        '''Email address not there, no user for you'''
        self.assertNone(User.user_from_email_address('no@such.address'))

    def test_user_from_any_address(self):
        '''Retrieve a user using any registered address, email or primary'''
        self.assertEqual(User.user_from_any_address(self.user.address).key(), self.user.key())
        self.assertEqual(User.user_from_any_address(self.address1).key(), self.user.key())
        self.assertEqual(User.user_from_any_address(self.address2).key(), self.user.key())
