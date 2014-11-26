__module_name__ = "Galgje"
__module_version__ = "0.2"
__module_description__ = "Bot waarmee galgje gespeeld kan worden. Reageert op het woord galgje."
__author__ = "Hans Kalle"



class Hangman:
	def __init__(self, player):
		self.player = player
		self.used_chars = set([])
		self.guesses_left = 7
		self.done = False
		self.won = False
	
	def startGame(self):
		import random
		wordlist = ["stootjuk", "wissel", "spoortak", "isolatielas", "profielvrij", "aankondigingstijd", "sein", "prorail", "services", "raildocs", "fuzzy", "overweginstallatie"]
		self.word = wordlist[random.randint(0,len(wordlist)-1)]
		return "Nou, " + self.player + ", ik heb een woord van " + str(len(self.word)) + " letters in gedachten. Roep maar een letter."

	def doMove(self, character):
		if not self.done:
			character = character.lower()
			if character in self.used_chars:
				return self.wrongMove("Je hebt de " + character + " al gebruikt, " + self.player + "!")
			else:
				self.used_chars.add(character)
				if character in self.word:
					return self.rightMove("Er zit inderdaad een " + character + " in het woord, " + self.player + ": ")
				else:
					return self.wrongMove("Er zit geen " + character + " in het woord, " + self.player + ".")
		else:
			if self.won:
				return "Je hebt het spel al gewonnen," + self.player + "."
			else:
				return "Je hebt het spel al verloren," + self.player + "."

	def wrongMove(self, message):
		self.guesses_left -= 1
		if self.guesses_left == 0:
			self.done = True
			self.won = False
			return message + " Helaas, je verliest. Het woord was " + self.word + "."
		else:
			return message + " Je hebt nog " + str(self.guesses_left) + " beurten over."

	def rightMove(self, message):
		missingCharacters = 0
		for character in self.word:
			if character in self.used_chars:
				message = message + character
			else:
				message = message + "."
				missingCharacters += 1
		message = message
		if missingCharacters == 0:
			message = message + ". Gefeliciteerd! Je hebt gewonnen."
			self.done = True
			self.won = True
		return message

	def isDone(self):
		return self.done



class HangmanGameDirector:
	def __init__(self, streamer):
		self.streamer = streamer
		self.games = {}

	def parse(self, nick, line):
		message = ''
		if self.hasActiveGameFor(nick):
			if self.singleCharacterResponse(line):
				game = self.games[nick]
				message = game.doMove(line)
				if game.isDone():
					self.endGame(nick)
		else:
			if "galgje" in line.split():
				game = self.newGame(nick)
				message = game.startGame()
		if message != '':
			self.streamer.output(message)

	def newGame(self, nick):
		game = Hangman(nick)
		self.games[nick] = game
		return game

	def endGame(self, nick):
		self.games.pop(nick)

	def pruneGames(self, activeNicks):
		for games in self.games:
			if games.player not in activeNicks:
				self.endGame(games.player)

	def hasActiveGameFor(self, nick):
		return nick in self.games

	def singleCharacterResponse(self, line):
		return len(line) == 1



import hexchat;

class HexchatStreamer:
	def output(self, message):
		hexchat.command("say " + message)

gameDirector = HangmanGameDirector(HexchatStreamer())

def onMessage(word, word_eol, userdata):
	try:
	  gameDirector.parse(word[0], word[1])
	  return hexchat.EAT_NONE
	except:
		hexchat.prnt('Fout bij het parsen van ' + word[0] + ': ' + word[1] + '.')

def onPart(word, word_eol, userdata):
	try:
		context = hexchat.find_context()
		activeUsers = context.get_list('users')
		activeNicks = [user.nick for user in activeUsers]
		gameDirector.pruneGames(activeNicks)
		return hexchat.EAT_NONE
	except:
		hexchat.prnt('Fout bij het parsen van ' + word[0] + ': ' + word[1] + '.')

hexchat.hook_print('Channel Message', onMessage)
hexchat.hook_print('Part', onPart)

hexchat.prnt(__module_name__ + ' version ' + __module_version__ + ' loaded.')
hexchat.prnt(__module_description__)