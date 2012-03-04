'''
Created on Mar 3, 2012

@author: pez
'''

from test import MooTestCase
import moo.utils as utils
class TextLinesToListTests(MooTestCase):
    '''Testing the textlines_to_list function'''
    def test_one_line(self):
        '''One line of text in results in a list with that line'''
        text = '''A line'''
        self.assertEqual([text], utils.textlines_to_list(text))

    def test_multiple_lines(self):
        '''X nonempty lines of text results in X lines'''
        line1, line2, line3, line4 = ('l1', 'l2', 'l3', 'l4')
        text = '''%s
        %s
        %s
        %s''' % (line1, line2, line3, line4)
        self.assertEqual([line1, line2, line3, line4], utils.textlines_to_list(text))

    def test_no_empty_lines(self):
        '''Empty lines are stripped away when building the taglines list'''
        text ='''
        
        '''
        self.assertEqual([], utils.textlines_to_list(text))
        line1, line2 = ('l1','l2')
        text = '''
        %s
        ''' % line1
        self.assertEqual([line1], utils.textlines_to_list(text))
        text = '''
        %s
        
        %s
        ''' % (line1, line2)
        self.assertEqual([line1, line2], utils.textlines_to_list(text))
