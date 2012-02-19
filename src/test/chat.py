#!/usr/bin/env python
# -*- coding: latin-1 -*-

from test import ModelTestCase
from moo.chat import Chat
from moo.user import User

class TestChatListeners(ModelTestCase):
    '''Tests for Chat listener functionality'''
    chat = None
    user1 = None
    user2 = None
    user3 = None
    
    def setUp(self):
        super(TestChatListeners, self).setUp()
        self.user1 = User.create(u'u1', u'u1@foo')
        self.user2 = User.create(u'u2', u'u2@foo')
        self.user3 = User.create(u'u3', u'u3@foo')
        self.chat = Chat.create(title=u'chat 1')
        self.chat.add_participant(self.user1.address)
        self.chat.add_participant(self.user2.address)
        self.chat.add_participant(self.user3.address)
        
    def test_default_listeners(self):
        '''A chat's listeners list is the same as the participants list by default'''
        self.assertEqual(set(self.chat.participants), set([u.address for u in self.chat.listeners]))

    def test_add_remove_listeners(self):
        '''Adding and removing listeners'''
        self.chat.add_listener(self.user1)
        self.test_default_listeners()
        self.chat.remove_listener(self.user1.address)
        self.assertEqual(set([u.key() for u in self.user2, self.user3]), set(u.key() for u in self.chat.listeners))

class TestChatTaglines(ModelTestCase):
    '''Tests for Chat taglines functionality'''
    chat = None
    user1 = None
    tagline1 = u'Foo'
    tagline2 = u'Bar'
    
    def setUp(self):
        super(TestChatTaglines, self).setUp()
        self.user1 = User.create(u'u1', u'u1@foo')
        self.chat = Chat.create(title=u'chat 1')
        self.chat.add_participant(self.user1.address)
        
    def test_default_taglines(self):
        self.assertEqual([], self.chat.taglines)

    def test_update_taglines_no_tagline(self):
        '''Update with an empty tagline text should result in an empty list of taglines'''
        self.chat.update_taglines('')
        self.assertEqual(self.chat.taglines, [])

    def test_update_taglines_one_line(self):
        '''One line of text in results in that line being the only tagline'''
        self.chat.update_taglines(self.tagline1)
        self.assertEqual([self.tagline1], self.chat.taglines)

    def test_update_taglines_multiple_lines(self):
        '''X nonempty lines of text results in X taglines'''
        self.chat.update_taglines('''%s
        %s
        %s
        %s''' % (self.tagline1, self.tagline2, self.tagline2, self.tagline1))
        self.assertEqual([self.tagline1, self.tagline2, self.tagline2, self.tagline1], self.chat.taglines)

    def test_update_taglines_no_empty_lines(self):
        '''Empty lines are stripped away when building the taglines list'''
        self.chat.update_taglines('''
        
        ''')
        self.assertEqual([], self.chat.taglines)
        self.chat.update_taglines('''
        %s
        ''' % self.tagline1)
        self.assertEqual([self.tagline1], self.chat.taglines)
        self.chat.update_taglines('''%s
        %s''' % (self.tagline1, self.tagline2))
        self.assertEqual([self.tagline1, self.tagline2], self.chat.taglines)

    def test_taglines_as_text(self):
        '''The taglines_as_text property returns all taglines as a string separating taglines using newline'''
        self.chat.update_taglines('''%s
        %s''' % (self.tagline1, self.tagline2))
        self.assertEqual('%s\n%s' % (self.tagline1, self.tagline2), self.chat.taglines_as_text)