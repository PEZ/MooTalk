#An XMPP on GAE experiment

import logging
import os
import wsgiref.handlers
from moo.user import User
from moo.chat import Chat
from google.appengine.api import users as GoogleUsers
from moo.xmpp_handler import XmppHandler

from google.appengine.ext import webapp
from google.appengine.ext.webapp import template

register = template.create_template_register()

@register.simple_tag
def chat_user_avatar(chat, participant):
    return Chat.chat_user(chat, participant).avatar

def admin_required(func):
    def wrapper(self, *args, **kw):
        if not GoogleUsers.is_current_user_admin():
            self.redirect(GoogleUsers.create_login_url(self.request.uri))
        else:
            func(self, *args, **kw)
    return wrapper

class WebHandler(webapp.RequestHandler):

    def Render(self, template_file, template_values, layout='main.html'):
        if layout == None:
            _template = template_file
        else:
            _template = layout
            template_values = dict(template_values, **{'template': template_file})
        path = os.path.join(os.path.dirname(__file__), 'templates', _template)
        self.response.out.write(template.render(path, template_values))

    def error(self, code):
        super(WebHandler, self).error(code)
        if code == 404:
            self.Render("404.html", {})

class ChatsHandler(WebHandler):
    @admin_required
    def post(self):
        action = self.request.get('action')
        if action == 'add_chat':
            name = self.request.get('name').strip()
            if name != '':
                Chat.create(name)
                    
        self.get()

    @admin_required
    def get(self):
        template_values = {
            'chats': Chat.all(),
        }
        self.Render("chats.html", template_values)

class ChatHandler(WebHandler):
    def _get_chat(self, _key_or_title):
        chat = Chat.chat_from_title(_key_or_title)
        if chat == None:
            try:
                chat = Chat.get(_key_or_title)
            except:
                logging.info("Invalid chat requested? (%s)" % _key_or_title)
        if chat == None:
            self.error(404)
        return chat

    @admin_required
    def post(self, _key_or_title):
        chat = self._get_chat(_key_or_title)
        chat.clean_chat_from_non_users()
        if chat != None:
            action = self.request.get('action')
            if action == 'delete_chat' and len(chat.participants) == 0:
                chat.delete()
            elif action == 'add_participant':
                chat.add_participant(self.request.get('address').strip())
            elif action == 'remove_participant':
                chat.remove_participant(self.request.get('participant'))
            elif action == 'update_taglines':
                chat.update_taglines(self.request.get('taglines'))
            self.get(_key_or_title)
                    

    @admin_required
    def get(self, _key_or_title):
        chat = self._get_chat(_key_or_title)
        if chat != None:
            chat.clean_chat_from_non_users()
            template_values = {
                'chat': chat,
                'users': User.all()
            }
            self.Render("chat.html", template_values)

class UsersHandler(WebHandler):
    @admin_required
    def post(self):
        delete_key = self.request.get('key').strip()
        nick = self.request.get('nick').strip()
        address = self.request.get('address').strip()
        
        if delete_key != '':
            User.murder(delete_key)
        elif address:
            User.create(nick, address)
        
        self.get()

    @admin_required
    def get(self):
        template_values = {
            'users': User.all(),
        }
        self.Render("users.html", template_values)

class IndexHandler(WebHandler):
    def get(self):
        template_values = {
        }
        self.Render("index.html", template_values)

class MooHandler(WebHandler):
    def get(self):
        template_values = {
        }
        self.Render("moo.html", template_values, None)

def main():
    app = webapp.WSGIApplication([
            ('/', IndexHandler),
            ('/moo/?', MooHandler),
            ('/chats/?', ChatsHandler),
            ('/chat/(.*?)/?', ChatHandler),
            ('/users/?', UsersHandler),
            ('/_ah/xmpp/message/chat/', XmppHandler),
            ], debug=True)
    wsgiref.handlers.CGIHandler().run(app)

if __name__ == '__main__':
    main()
