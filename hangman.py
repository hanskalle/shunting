__module_name__ = "Galgje"
__module_version__ = "0.2"
__module_description__ = "Bot waarmee galgje gespeeld kan worden. Reageert op het woord galgje."
__author__ = "DaneelBaley"

class Hangman:
	def __init__(this, player):
		import random;
		wordlist = ["stootjuk", "wissel", "spoortak", "isolatielas", "profielvrij", "aankondigingstijd", "sein", "overweginstallatie"]
		this.player = player
		this.word = wordlist[random.randint(0,len(wordlist)-1)]
		this.used_chars = set([])
		this.guesses_left = 7
		this.done = False
		this.won = False
	
	def startGame(this):
		return "Nou, " + this.player + ", ik heb een woord van " + str(len(this.word)) + " letters in gedachten. Roep maar een letter."

	def isDone(this):
		return this.done

	def doMove(this, character):
		if this.done:
			if this.won:
				return "Je hebt het spel al gewonnen," + this.player + "."
			else:
				return "Je hebt het spel al verloren," + this.player + "."
		else:
			character = character.lower()
			if character in this.used_chars:
				return this.wrongMove("Je hebt de " + character + " al gebruikt, " + this.player + "!")
			else:
				this.used_chars.add(character)
				if character in this.word:
					return this.rightMove("Er zit inderdaad een " + character + " in het woord, " + this.player + ": ")
				else:
					return this.wrongMove("Er zit geen " + character + " in het woord, " + this.player + ".")

	def wrongMove(this, message):
		this.guesses_left -= 1
		if this.guesses_left == 0:
			this.done = True
			this.won = False
			return message + " Helaas, je verliest. Het woord was " + this.word + "."
		else:
			return message + " Je hebt nog " + str(this.guesses_left) + " beurten over."

	def rightMove(this, message):
		missing_chars = 0
		for character in this.word:
			if character in this.used_chars:
				message = message + character
			else:
				missing_chars += 1
				message = message + "."
		message = message
		if missing_chars == 0:
			message = message + ". Gefeliciteerd! Je hebt gewonnen."
			this.done = True
			this.won = True
		return message

class HangmanGameDirector:
	def __init__(this, streamer):
		this.games = {}
		this.streamer = streamer

	def parse(this, nick, line):
		message = ''
		if this.hasActiveGameFor(nick):
			if this.singleCharacterResponse(line):
				message = this.games[nick].doMove(line)
				if this.games[nick].isDone():
					this.endGame(nick)
		else:
			if "galgje" in line.split():
				this.newGame(nick)
				message = this.games[nick].startGame()
		if message != '':
			this.streamer.output(message)
			
	def pruneGames(this, activeUsers):
		for games in this.games:
			if games.player not in activeUsers:
				this.endGame(games.player)

	def hasActiveGameFor(this, nick):
		return nick in this.games

	def singleCharacterResponse(this, line):
		return len(line) == 1

	def newGame(this, nick):
		this.games[nick] = Hangman(nick)

	def endGame(this, nick):
		this.games.pop(nick)


import hexchat;

class HexchatStreamer:
	def output(this, message):
		hexchat.command("say " + message)

gameDirector = HangmanGameDirector(HexchatStreamer())

def check_line(word, word_eol, userdata):
	try:
	  gameDirector.parse(word[0], word[1])
	  return hexchat.EAT_NONE
	except:
		hexchat.prnt('Fout bij het parsen van ' + word[0] + ': ' + word[1] + '.')

hexchat.hook_print('Channel Message', check_line)
hexchat.prnt(__module_name__ + ' version ' + __module_version__ + ' loaded.')
hexchat.prnt(__module_description)