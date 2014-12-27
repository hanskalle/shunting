#!/usr/bin/python

__module_name__ = "Shunting"
__module_version__ = "0.1"
__module_description__ = "Bot waarmee shunting gespeeld kan worden. Reageert op het woord shunting."
__author__ = "Hans Kalle"

import hexchat
from ShuntingGame import ShuntingGame
from ShuntingDirector import ShuntingDirector

class HexchatStreamer():
    def output(self, line):
		hexchat.command("say " + line)

    def privateOutput(self, nick, line):
		hexchat.command("msg %s %s" % (nick, line))

gameDirector = ShuntingDirector(HexchatStreamer())

def onMessage(word, word_eol, userdata):
	try:
	  gameDirector.parse(word[0], word[1])
	  return hexchat.EAT_NONE
	except:
		hexchat.prnt('Fout bij het parsen van ' + word[0] + ': ' + word[1] + '.')
		return hexchat.EAT_NONE

def onPart(word, word_eol, userdata):
	try:
		context = hexchat.find_context()
		activeUsers = context.get_list('users')
		activeNicks = [user.nick for user in activeUsers]
		#gameDirector.pruneGames(activeNicks)
		return hexchat.EAT_NONE
	except:
		hexchat.prnt('Fout bij het verwerken van part-notificatie ' + word[0] + ': ' + word[1] + '.')
		return hexchat.EAT_NONE

hexchat.hook_print('Channel Message', onMessage)
hexchat.hook_print('Part', onPart)

hexchat.prnt(__module_name__ + ' version ' + __module_version__ + ' loaded.')
hexchat.prnt(__module_description__)