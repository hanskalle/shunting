__module_name__ = "HanabiGame"
__module_version__ = "1.1"
__module_description__ = "Hanabi Game."


class HanabiGame:
    SETUP = 1
    ON = 2
    OVER = 3

    COLORS = "ROGBP"
    MAX_HINTS = 8
    MAX_THUNDERSTORMS = 3
    MIN_PLAYERS = 2
    MAX_PLAYERS = 5
    MAX_SCORE = len(COLORS) * 5

    def __init__(self, owner):
        self._state = self.SETUP
        self._activePlayer = None
        self._hints = self.MAX_HINTS
        self._thunderstorms = self.MAX_THUNDERSTORMS
        self._initDeck()
        self._initDiscardPile()
        self._initFireworks()
        self._initPlayers()
        self.addPlayer(owner)

    def _initDeck(self):
        self._generateDeck()
        self._shuffleDeck()

    def _generateDeck(self):
        self._deck = []
        for color in self.COLORS:
            for i in range(3):
                self._deck.append(color + "1")
            for i in range(2):
                for number in range(2, 5):
                    self._deck.append(color + str(number))
            self._deck.append(color + "5")

    def _shuffleDeck(self):
        import random
        random.shuffle(self._deck)

    def _getCardFromDeck(self):
        if len(self._deck) == 0:
            Exception("Cannot draw from empty deck.")
        return self._deck.pop()

    def _removeCardFromDeck(self, card):
        self._deck.remove(card)

    def _setupDeckForTest(self, cards):
        if not self.isSettingUp():
            raise Exception("Can only setup the deck when in setup phase.")
        for card in cards:
            self._deck.remove(card)
        while len(cards) > 0:
            self._deck.append(cards.pop())

    def _dealCards(self):
        for player in self._players:
            while len(self._hands[player]) < self.getMaxHandCards():
                newCard = self._getCardFromDeck()
                self._hands[player].append(newCard)

    def _initDiscardPile(self):
        self._discardPile = []

    def _initPlayers(self):
        self._players = []
        self._hands = {}
        self._activePlayer = None

    def addPlayer(self, newPlayer):
        if not self.isSettingUp():
            raise Exception("Game only accepts extra players at setup.")
        if newPlayer in self.getPlayers():
            raise Exception("You cannot add a player twice.")
        if len(self._players) == self.MAX_PLAYERS:
            raise Exception("The game has a maximum of 5 players.")
        self._players.append(newPlayer)
        self._hands[newPlayer] = []

    def removePlayer(self, player):
        if not self.isSettingUp():
            raise Exception("You can only remove players at setup.")
        if player not in self._players:
            raise Exception("You can only remove existing players.")
        if player == self._players[0]:
            raise Exception("You must not remove the owner of the game.")
        self._players.remove(player)
        del (self._hands[player])

    def getOwner(self):
        return self._players[0]

    def getPlayers(self):
        return self._players

    def getNumberOfPlayers(self):
        return len(self._players)

    def getActivePlayer(self):
        return self._activePlayer

    def getHandCards(self, player):
        return self._hands[player]

    def getMaxHandCards(self):
        if self.getNumberOfPlayers() <= 3:
            return 5
        else:
            return 4

    def getNumberOfHandCards(self, player=None):
        if player is None:
            player = self._activePlayer
        return len(self._hands[player])

    def getNumberOfCardsInDeck(self):
        return len(self._deck)

    def _setupHandForTest(self, player, cards):
        if not self.isSettingUp():
            raise Exception("Can only setup a hand when in setup phase.")
        for card in cards:
            self._removeCardFromDeck(card)
            self._addCardToHand(card, player)

    def _addCardToHand(self, card, player):
        self._hands[player].append(card)

    def reorderHandCards(self, player, order):
        oldHand = self._hands[player]
        numberOfHandCards = len(oldHand)
        if len(order) != len(oldHand):
            raise Exception("Reordening does not match the number of hand cards.")
        for i in range(numberOfHandCards - 1):
            index = order[i]
            if index < 1 or numberOfHandCards < index:
                raise Exception("Reordering index out of bound.")
            if index in order[i + 1:]:
                raise Exception("Reordering indexes should be unique.")
        self._hands[player] = []
        for index in order:
            self._hands[player].append(oldHand[index - 1])

    def _initFireworks(self):
        self._Fireworks = {}
        for color in self.COLORS:
            self._Fireworks[color] = []

    def getFireworkLength(self, color):
        return len(self._Fireworks[color])

    def _canBeAddedToFirework(self, card):
        color = self.getCardColor(card)
        number = self._getCardNumber(card)
        return self.getFireworkLength(color) == number - 1

    def _addToFirework(self, card):
        if not self._canBeAddedToFirework(card):
            raise Exception("Card cannot be added to a firework.")
        color = self.getCardColor(card)
        self._Fireworks[color].append(card)
        if self.getFireworkLength(color) == 5:
            self._increaseHints()

    def _setupFireworksForTest(self, cards):
        if not self.isSettingUp():
            raise Exception("Can only setup fireworks when in setup phase.")
        for card in cards:
            self._deck.remove(card)
            self._addToFirework(card)

    def getThunderstormsLeft(self):
        return self._thunderstorms

    def _decreaseThunderstorms(self):
        if self._thunderstorms > 0:
            self._thunderstorms -= 1

    def getHintsLeft(self):
        return self._hints

    def _decreaseHints(self):
        if self._hints > 0:
            self._hints -= 1

    def _increaseHints(self):
        if self._hints < self.MAX_HINTS:
            self._hints += 1

    def getState(self):
        return self._state

    def isSettingUp(self):
        return self._state == self.SETUP

    def isOn(self):
        return self._state == self.ON

    def isOver(self):
        return self._state == self.OVER

    def canStart(self):
        if not self.isSettingUp():
            return False
        if self.getNumberOfPlayers() < self.MIN_PLAYERS:
            return False
        return True

    def isComplete(self):
        return self.getScore() == self.MAX_SCORE

    def start(self):
        if not self.canStart():
            raise Exception("Game cannot start.")
        self._dealCards()
        self._state = self.ON
        self._activePlayer = self._players[0]

    def isLastRound(self):
        return self.getNumberOfCardsInDeck() == 0

    def _nextTurn(self):
        if not self.isOn():
            raise Exception("Game is not on.")
        self._activateNextPlayer()

    def _setGameOver(self):
        self._state = self.OVER

    def discard(self, index):
        if not self.isOn():
            raise Exception("You cannot discard a card when the game is not running.")
        if index > len(self._hands[self._activePlayer]):
            raise Exception("You cannot discard a card you do not have.")
        card = self._getAndRemoveCardFromHandRepleting(index)
        self._discardPile.append(card)
        self._increaseHints()
        self._nextTurn()

    @staticmethod
    def getCardColor(card):
        return card[0]

    @staticmethod
    def _getCardNumber(card):
        return int(card[1])

    def _getAndRemoveCardFromHandRepleting(self, index):
        card = self._hands[self._activePlayer][index - 1]
        del (self._hands[self._activePlayer][index - 1])
        if not self.isLastRound():
            newCard = self._getCardFromDeck()
            self._hands[self._activePlayer].insert(index - 1, newCard)
        else:
            self._discardHand()
        return card

    def play(self, index):
        if not self.isOn():
            raise Exception("You cannot play a card when the game is not running.")
        if index > len(self._hands[self._activePlayer]):
            raise Exception("You cannot play a card you do not have.")
        card = self._getAndRemoveCardFromHandRepleting(index)
        if self._canBeAddedToFirework(card):
            self._addToFirework(card)
            if self.isComplete():
                self._setGameOver()
            else:
                self._nextTurn()
            return True
        else:
            self._decreaseThunderstorms()
            if self.getThunderstormsLeft() > 0:
                self._nextTurn()
            else:
                self._setGameOver()
            return False

    def hint(self, player, hint):
        if not self.isOn():
            raise Exception("You cannot hint when the game is not running.")
        if player == self._activePlayer:
            raise Exception("One cannot hint itself.")
        if self.getHintsLeft() == 0:
            raise Exception("No hints left.")
        self._decreaseHints()
        matches = []
        for card in self._hands[player]:
            matches.append(hint in card)
        self._nextTurn()
        return matches

    def _discardHand(self):
        while self.getNumberOfHandCards() > 0:
            card = self._hands[self._activePlayer].pop()
            self._discardPile.append(card)

    def _activateNextPlayer(self):
        index = self._players.index(self._activePlayer) + 1
        if index >= len(self._players):
            index = 0
        nextPlayer = self._players[index]
        if self.getNumberOfHandCards(nextPlayer) == 0:
            self._setGameOver()
        else:
            self._activePlayer = nextPlayer

    def _peekHandCard(self, index, player=None):
        if player is None:
            player = self._activePlayer
        return self._hands[player][index - 1]

    def getScore(self):
        score = 0
        for color in self.COLORS:
            score += self.getFireworkLength(color)
        return score
