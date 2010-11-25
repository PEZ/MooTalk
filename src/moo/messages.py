MESSAGE = "%s: %s"
MUTE_MESSAGE = "Chat Muted. You will not be sent broadcasted messages (don't forget to unmute)"
UNMUTE_MESSAGE = "Chat unmuted."
SHOUT_MESSAGE = "%s SHOUTS: %s"
ME_MESSAGE = "*%s* %s"
PRIVATE_MESSAGE = "-> *%s* %s"
SYSTEM_MESSAGE = "*** Moo! %s"
HELP_MSG = SYSTEM_MESSAGE % """
Mute all broadcasted messages (unless /shout is used):
/mute
/unmute

Shouts reaches all participants even if they have muted the chat:
/shout <message>

Private messages (/pm and /msg do the same thing):
/pm <nickname> <message>
/msg <nickname> <message>
/pm <address> <message>
/msg <address> <message>

Information about channel participants:
/who
/who am i
/who online

Referencing yourself:
/me <message>"""

NO_ACCESS = """You do not have access to this channel.

MooTalk is experimental. If you think you should have access, check:
- the address of the MooTalk bot you're talking too (stuff before the @ in the address.
- that your Jabber address matches that which is registered in the MooTalk user list (check this with whoever invited you)."""