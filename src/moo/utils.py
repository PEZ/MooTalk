'''
Created on Mar 3, 2012

@author: pez
'''

from google.appengine.api.app_identity import get_application_id

def get_appname():
    return get_application_id()

def textlines_to_list(text):
    """Takes a chunk of text, splits it up on newlines, removes empty lines returns a list of lines."""
    return [line.strip() for line in text.split('\n') if line.strip() != '']
