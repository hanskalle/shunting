class ShuntingGame:
    SETUP = 1
    ON = 2
    OVER = 3
    
    COLORS = "ROGBP"
    MAX_HINTS = 8
    MAX_EXTRALOCOMOTIVES = 3
    MIN_PLAYERS = 2
    MAX_SCORE = len(COLORS) * 5
    
    def __init__(self, owner):
        self._state = ShuntingGame.SETUP
        self._hints = ShuntingGame.MAX_HINTS
        self._extraLocomotives = ShuntingGame.MAX_EXTRALOCOMOTIVES
        self._initDeck()
        self._initDiscardPile()
        self._initTrains()
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
                for number in range(2,5):
                    self._deck.append(color + str(number))
            self._deck.append(color + "5")

    def _shuffleDeck(self):
        import random
        random.shuffle(self._deck)

    def _getNumberOfCardsInDeck(self):
        return len(self._deck)

    def _getCardFromDeck(self):
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

    def _dealNewCardTo(self, player):
        card = self._getCardFromDeck()
        self._hands[player].append(card)

    def _dealCards(self):
        for player in self._players:
            while len(self._hands[player]) < self._getMaxHandCards():
                self._dealNewCardTo(player)

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
        self._players.append(newPlayer)
        self._hands[newPlayer] = []

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
        
    def getNumberOfHandCards(self, player=None):
        if player is None:
            player = self._activePlayer
        return len(self._hands[player])

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
        for i in range(numberOfHandCards-1):
            index = order[i]
            if index < 1 or numberOfHandCards < index:
                raise Exception("Reordering index out of bound.")
            if index in order[i+1:]:
                raise Exception("Reordering indexes should be unique.")
        self._hands[player] = []
        for index in order:
            self._hands[player].append(oldHand[index-1])

    def _initTrains(self):
        self._trains = {}
        for color in self.COLORS:
            self._trains[color] = []

    def getTrainLength(self, color):
        return len(self._trains[color])

    def _canBeAddedToTrain(self, card):
        color = self.getCardColor(card)
        number = self._getCardNumber(card)
        return self.getTrainLength(color) == number - 1

    def _addToTrain(self, card):
        if not self._canBeAddedToTrain(card):
           raise Exception("Card cannot be added to a train.")
        color = self.getCardColor(card)
        self._trains[color].append(card)
        if self.getTrainLength(color) == 5:
            self._increaseHints()

    def _setupTrainsForTest(self, cards):
        if not self.isSettingUp():
            raise Exception("Can only setup trains when in setup phase.")
        for card in cards:
            self._deck.remove(card)
            self._addToTrain(card)

    def getExtraLocomotivesLeft(self):
        return self._extraLocomotives
        
    def _decreaseExtraLocomotives(self):
        if self._extraLocomotives > 0:
            self._extraLocomotives -= 1

    def getHintsLeft(self):
        return self._hints

    def _decreaseHints(self):
        if self._hints > 0:
            self._hints -= 1

    def _increaseHints(self):
        if self._hints < ShuntingGame.MAX_HINTS:
            self._hints += 1

    def _getMaxHandCards(self):
        if self.getNumberOfPlayers() <= 3:
            return 5
        else:
            return 4

    def getState(self):
        return self._state

    def isSettingUp(self):
        return self._state == ShuntingGame.SETUP

    def isOn(self):
        return self._state == ShuntingGame.ON

    def isOver(self):
        return self._state == ShuntingGame.OVER

    def canStart(self):
        if not self.isSettingUp():
            return False
        if self.getNumberOfPlayers() < ShuntingGame.MIN_PLAYERS:
            return False
        return True

    def isComplete(self):
        return self.getScore() == ShuntingGame.MAX_SCORE

    def start(self):
        if not self.canStart():
            raise Exception("Game cannot start.")
        self._dealCards()
        self._state = ShuntingGame.ON
        self._activePlayer = self._players[0]

    def _isLastRound(self):
        return self._getNumberOfCardsInDeck() ==0

    def _nextTurn(self):
        if not self.isOn():
            raise Exception("Game is not on.")
        if self._isLastRound():
            self._discardHand()
        else:
            self._repleteHand()
        self._activateNextPlayer()

    def _setGameOver(self):
        self._state = ShuntingGame.OVER

    def discard(self, index):
        if not self.isOn():
            raise Exception("You cannot discard a card when the game is not running.")
        if index > len(self._hands[self._activePlayer]):
            raise Exception("You cannot discard a card you do not have.")
        card = self._getAndRemoveCardFromHand(index)
        self._discardPile.append(card)
        self._increaseHints()
        self._nextTurn()

    def getCardColor(self, card):
        return card[0]

    def _getCardNumber(self, card):
        return int(card[1])

    def _getAndRemoveCardFromHand(self, index):
        card = self._hands[self._activePlayer][index-1]
        del self._hands[self._activePlayer][index-1]
        return card

    def play(self, index):
        if not self.isOn():
            raise Exception("You cannot play a card when the game is not running.")
        if index > len(self._hands[self._activePlayer]):
            raise Exception("You cannot play a card you do not have.")
        card = self._getAndRemoveCardFromHand(index)
        if self._canBeAddedToTrain(card):
            self._addToTrain(card)
            if self.isComplete():
                self._setGameOver()
            else:
                self._nextTurn()
            return True
        else:
            self._decreaseExtraLocomotives()
            if self.getExtraLocomotivesLeft() > 0:
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
            card = self._getAndRemoveCardFromHand(1)
            self._discardPile.append(card)

    def _repleteHand(self):
        while self.getNumberOfHandCards() < self._getMaxHandCards() and self._getNumberOfCardsInDeck() > 0:
            self._dealNewCardTo(self._activePlayer)

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
        return self._hands[player][index-1]

    def getScore(self):
        score = 0
        for color in ShuntingGame.COLORS:
            score += self.getTrainLength(color)
        return score
