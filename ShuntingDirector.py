#!/usr/bin/python

from ShuntingGame import ShuntingGame

class ShuntingDirector():
    def __init__(self, streamer):
       self._streamer = streamer
       self._games = []
       self._initCommands()

    def _initCommands(self):
        self._commands = [
            _Command(None, False, "(.* )?shunting spelen.*[^?]$", self._createNewGame),
            _Command(None, False, ".*regels( .*)? shunting.*\?$", self._showRules),
            _Command(None, False, ".*shunting", self._showStartingInstructions),
            _Command(None, False, ".*ik doe mee met (?P<owner>[A-Za-z_\-0-9]+)", self._joinGame),
            _Command(ShuntingGame.SETUP, False, ".*we (.*)?beginnen[^?]$", self._startGame),
            _Command(ShuntingGame.ON, True, ".*leg( .*)? (?P<index>[1-5])( .*)? (af|weg)", self._discard),
            _Command(ShuntingGame.ON, True, ".*leg( .*)? (?P<index>[1-5])( .*)? (neer|aan|bij)", self._play),
            _Command(ShuntingGame.ON, True, ".*speel( .*)? (?P<index>[1-5])", self._play),
            _Command(ShuntingGame.ON, True, ".*hint (speler )?(?P<player>[A-Za-z_\-0-9]+)(: ?| )?(.+ )?((cijfer|getal) )?(.+ )?(?P<hint>[1-5])", self._hint),
            _Command(ShuntingGame.ON, True, ".*hint (speler )?(?P<player>[A-Za-z_\-0-9]+)(: ?| )?(.+ )?(kleur )?(.+ )?(?P<hint>[rogbp])", self._hint),
            _Command(ShuntingGame.ON, True, ".*hint (.+ )?((cijfer|getal) )?(.+ )?(?P<hint>[1-5]) (aan|voor) (speler )?(?P<player>[A-Za-z_\-0-9]+)", self._hint),
            _Command(ShuntingGame.ON, True, ".*hint (.+ )?(kleur )?(.+ )?(?P<hint>[rogbp])(ood|ranje|roen|lauw|aars)? (aan|voor) (speler )?(?P<player>[A-Za-z_\-0-9]+)", self._hint),
            _Command(ShuntingGame.ON, [True, False], "(help|hulp|om hulp)(!+|.)$", self._showHelp),
            _Command(ShuntingGame.ON, [True, False], ".*orden (.* )?(?P<order>[1-5]{4,5})", self._reorder),
            _Command([ShuntingGame.SETUP, ShuntingGame.ON], [True, False], "(.* )?shunting spelen.*[^?]$", self._stillPlayingAnotherGame),
            _Command([ShuntingGame.SETUP, ShuntingGame.ON], [True, False], ".*ik (.* )?mee ((.+|met) )?(?P<owner>[A-Za-z_\-0-9]+)", self._stillPlayingAnotherGame),
            _Command([ShuntingGame.SETUP, ShuntingGame.ON], [True, False], ".*hints.*\?$", self._showHints),
            _Command([ShuntingGame.SETUP, ShuntingGame.ON], [True, False], ".*noodloc.*\?$", self._showExtraLocomotives),
            _Command([ShuntingGame.SETUP, ShuntingGame.ON], [True, False], ".*treinen.*\?$", self._showTrains),
            _Command([ShuntingGame.SETUP, ShuntingGame.ON], [True, False], ".*regels.*\?$", self._showRules)]

    def parse(self, nick, line):
        line = line.lower()
        game = self._getGame(nick)
        if game:
            gameState = game.getState()
            isActive = (nick == game.getActivePlayer())
        else:
            gameState = None
            isActive = False
        for command in self._commands:
            match = command.match(gameState, isActive, line)
            if match:
                dict = match.groupdict()
                dict["nick"] = nick
                command.function(game, nick, dict)
                break

    def _getGame(self, nick):
        gameFound = None
        for game in self._games:
            for player in game.getPlayers():
                if nick == player.lower():
                    gameFound = game
                    break
        return gameFound

    def _showStartingInstructions(self, game, nick, dict):
        self._output([
            "Ik ben een bot die het spelletje shunting kan faciliteren!",
            "Op de volgende manieren kun je shunting bijvoorbeeld starten:",
            "  Laten we shunting spelen.",
            "  Ik wil graag shunting spelen.",
            "Maar je kunt ook eerst vragen om de spelregels van shunting"])

    def _showHelp(self, game, nick, dict):
        self._output([
            "In je beurt heb je drie mogelijkheden:",
            "1) Speel kaart <index>. Bijvoorbeeld: Speel kaart 2. Of: Ik speel 2.",
            "2) Leg kaart <index> af. Bijvoorbeeld: Leg kaart 2 af. Of: Ik leg 4 weg.",
            "3) Hint <kleur/cijfer> aan <nick>. Bijvoorbeeld: Hint rood aan David. Of: Hint David: 3",
            "In en buiten je beurt kun je de volgende dingen doen.",
            "- Orden hand 35124. Hiermee verwissel je de volgorde van je handkaarten. Dat kan helpen bij het onthouden van de hints.",
            "- Welke treinen hebben we nu?",
            "- Hoeveel hints zijn er nog beschikbaar?",
            "- Wat is het aantal noodlocomotieven dat we nog mogen inzetten?",
            "- Kun je de spelregels nog een keer precies vertellen?",
            "Ook deze vragen mag je korter formuleren, hoor. En als je ze vergeten bent, roep dan maar om hulp."])

    def _createNewGame(self, game, nick, dict):
        self._games.append(ShuntingGame(nick))
        self._output([
            "Nou, %(nick)s, leuk dat je shunting wil spelen. Wie doet er mee? Er is minimaal nog 1 speler nodig.",
            "Zeg 'Ik doe mee met %(nick)s.'."], dict)

    def _joinGame(self, game, nick, dict):
        game = self._getGame(dict["owner"])
        if game:
            if not nick in game.getPlayers():
                game.addPlayer(nick)
                dict["number_of_players"] = str(game.getNumberOfPlayers())
                self._output([
                    "Hoi %(nick)s, leuk dat je meedoet met het shunting spel van %(owner)s.",
                    "We hebben nu %(number_of_players)s spelers.",
                    "%(owner)s, zeg jij wanneer we beginnen?"], dict)
            else:
                self._output(["Maar %(nick)s, je doet al mee met het shunting spel van %(owner)s!"], dict)
        else:
            self._output([
                "Sorry %(nick)s, maar er is geen spel dat gestart is door %(owner)s."], dict)

    def _stillPlayingAnotherGame(self, game, nick, dict):
        players = ", ".join(game.getPlayers())
        dict["players"] = players
        self._output(["Sorry %(nick)s, je speelt al een spel met %(players)s!"], dict)

    def _startGame(self, game, nick, dict):
        if nick == game.getOwner():
            game.start()
            self._output(["Ik vertel de handkaarten via prive-berichten, zodat je als rangeerder niet weet welke wagons er op jouw opstelterrein staan."], dict)
            for player in game.getPlayers():
                self._tellHandToOthers(player, game)
            self._tellExtraLocomotives(game)
            self._tellHints(game)
            self._showHelp(game, nick, dict)
            self._tellTurn(game)
        else:
            dict["owner"] = game.getOwner()
            self._output(["Sorry %(nick)s, alleen %(owner)s mag een spel laten beginnen."], dict)

    def _discard(self, game, nick, dict):
        index = int(dict["index"])
        game.discard(index)
        if game.isOn():
            self._tellHandToOthers(nick, game)
            self._tellHints(game)
        self._nextTurn(game)

    def _play(self, game, nick, dict):
        index = int(dict["index"])
        card = game.getHandCards(nick)[index-1]
        dict["card"] = card
        self._output(["Jouw kaart %(index)s is een %(card)s."], dict)
        if game.play(index):
            color = game.getCardColor(card)
            self._tellTrains(game, color)
        else:
            self._output(["Die kan niet worden aangelegd en beland op de aflegstapel."], dict)
            self._tellExtraLocomotives(game)
        if game.isOn():
            self._tellHandToOthers(nick, game)
        self._nextTurn(game)

    def _hint(self, game, nick, dict):
        if game.getHintsLeft() > 0:
            hint = dict["hint"].upper()
            player = self._getProperPlayerName(game, dict["player"])
            if player != nick:
                if player in game.getPlayers():
                    matches = game.hint(player, hint)
                    indices = self._getMatchIndices(matches)
                    dict["indices"] = indices
                    dict["player"] = player
                    dict["hint"] = hint
                    if len(indices) == 0:
                        self._output(["%(player)s heeft geen %(hint)s's."], dict)
                    elif len(indices) == 1:
                        self._output(["Kaart %(indices)s van %(player)s is een %(hint)s."], dict)
                    else:
                        self._output(["De kaarten %(indices)s van %(player)s zijn %(hint)s-en."], dict)
                    self._tellHints(game)
                    self._nextTurn(game)
                else:
                    self._output(["Sorry %(nick)s er is geen speler die %(player)s heet. Probeer opnieuw."], dict)
            else:
                 self._output(["Jammer %(nick)s, maar jezelf hinten is niet toegestaan. Probeer opnieuw."], dict)
        else:
            self._output(["Jammer %(nick)s, maar er mogen nu geen hints meer gegegeven worden. Pas na het afleggen van een kaart mag dat weer. Probeer opnieuw."], dict)

    def _reorder(self, game, nick, dict):
        numberOfHandCards = len(game.getHandCards(nick))
        order = self._getIndicesList(dict["order"], numberOfHandCards)
        if len(order) == numberOfHandCards:
            game.reorderHandCards(nick, order)
            self._output(["De handkaarten van %(nick)s zijn opnieuw gerangschikt."], dict)
            self._tellHandToOthers(nick, game)
        else:
            dict["order"] = "54321"[-numberOfHandCards:]
            self._output(["De opgegeven ordening klopt niet. Voor een omgekeerde volgorde geeft je bijvoorbeeld %(order)s op."], dict)

    def _getIndicesList(self, indicesString, maxIndex):
        indicesList = []
        for index in indicesString:
            if not index in indicesList:
                index = int(index)
                if index <= maxIndex:
                    indicesList.append(index)
        return indicesList

    def _showHints(self, game, nick, dict):
        if game.isOn():
            self._tellHints(game)
        else:
            self._output(["Initieel zijn er 8 hints beschikbaar. Maar op dit moment is het spel nog niet begonnen."], dict)

    def _showTrains(self, game, nick, dict):
        if game.isOn():
            self._tellTrains(game)
        else:
            self._output(["Initieel hebben alle treinen 0 wagons. Maar op dit moment is het spel nog niet begonnen."], dict)

    def _showExtraLocomotives(self, game, nick, dict):
        if game.isOn():
            self._tellExtraLocomotives(game)
        else:
            self._output(["Initieel kan driemaal een noodlocomotief worden ingezet. Maar op dit moment is het spel nog niet begonnen."], dict)

    def _showRules(self, game, nick, dict):
        self._output(["De spelregels zijn erg eenvoudig.",
            "CONTEXT: Op Kijfhoek is het een drukte van belang. Van alle wagons die aankomen moeten verschillende treinen worden samengesteld. Iedere trein heeft een eigen kleur en de wagons moeten in de juiste volgorde worden aangekoppeld. Samen met je collega rangeerders heb je maar een nacht om de treinen op orde te krijgen!",
            "DOEL: De rangeerders bouwen samen vijf goederentreinen in de kleuren van de vervoerders: R(ood), O(ranje), G(roen), B(lauw) en P(aars). Elke trein krijgt 5 wagons, genummerd 1 tot en met 5. Probeer samen de treinen zo compleet mogelijk te maken.",
            "VERLOOP: Om beurten speel je kaarten (de wagons) en geef je elkaar hints. Iedere speler krijgt handkaarten (je eigen opstelterrein), maar alleen de andere spelers krijgen te zien welke wagons daarop staan. Verder staan er nog wagons in de wachtrij (de trekstapel).",
            "BEURT: Tijdens je beurt kies je uit drie mogelijkheden:",
            "1) Geef een hint aan een medespeler. Kies een kleur of een getal en vertel je medespeler welke van zijn of haar wagons daaraan voldoen. Maar let op: je hebt initieel maar 8 hints beschikbaar.",
            "2) Leg een kaart af en vul je hand weer aan. En als er minder dan 8 hints over zijn, komt er weer een hint bij.",
            "3) Speel een kaart om een trein te starten of te verlengen. De kleur moet kloppen en de nummers van de wagons moeten netjes oplopen. Maak je een trein compleet en resten er minder dan 8 hints, komt er weer een hint bij. Maar kan de gespeelde wagon niet worden aangelegd, dan moet die weg worden gerangeerd door een noodlocomotief. In alle gevallen vul je je hand weer aan.",
            "EINDE: Het spel eindigt als:",
            "a) Jullie alle treinen compleet hebt (wauw!).",
            "b) De derde noodlocomotief is ingezet.",
            "c) Nadat de laatste kaart getrokken is: dan krijgt iedereen, inclusief de rangeerder die de laatste kaart trok, nog 1 beurt.",
            "SCORE: De score is het totaal aantal wagons in de opgebouwde treinen.",
            "NOTA BENE: Er zijn van elke kleur drie wagons met het cijfer 1, twee met 2, 3 en 4 en slechts een enkele met een 5."], dict)

    def _nextTurn(self, game):
        if game.isOn():
            self._tellTurn(game)
        else:
            self._tellGameOver(game)

    def _tellGameOver(self, game):
        score = game.getScore();
        self._output(["Het spel is afgelopen.",
            "Jullie hebben in totaal %i wagons correct opgesteld." % score])
        if score <= 5:
            self._output(["Dat is een vreselijk beroerd resultaat! Zoek maar een baan als manager."])
        elif score <= 10:
            self._output(["Dat is eigenlijk wel erg slecht! Misschien is software ontwikkelaar wel wat voor je?"])
        elif score <= 15:
            self._output(["Dat begint ergens op te lijken. Blijf oefenen!"])
        elif score <= 20:
            self._output(["Een nette score. Maar ik voel dat er meer in dit team zit!"])
        elif score <= 24:
            self._output(["Geweldig. Zou je met dit team ook de 25 kunnen halen?"])
        else:
            self._output(["Legendarisch!!!!!"])
        self._removeGame(game.getOwner())
        
    def _removeGame(self, owner):
        for i in range(len(self._games)):
            if self._games[i].getOwner() == owner:
                del(self._games[i])
                break

    def _tellHandToOthers(self, player, game):
        hand = ",".join(game.getHandCards(player))
        for another in game.getPlayers():
            if another != player:
                self._privateOutput(another, "De hand van %s: %s." % (player, hand))

    def _tellExtraLocomotives(self, game):
        if game.getExtraLocomotivesLeft() > 1:
            self._output(["Er zijn nog %i noodlocomotieven om foute wagons af te rangeren." % game.getExtraLocomotivesLeft()])
        elif game.getExtraLocomotivesLeft() == 1:
            self._output(["Er is nog maar 1 noodlocomotief om foute wagons af te rangeren."])
        else:
            self._output(["Er zijn geen noodlocomotieven meer. Het spel is afgelopen!"])

    def _tellHints(self, game):
        if game.getHintsLeft() > 1:
            self._output(["Er mogen nog %i hints gegeven worden." % game.getHintsLeft()])
        elif game.getHintsLeft() == 1:
            self._output(["Er mag nog 1 hint gegeven worden."])
        else:
            self._output(["Er mogen geen hints gegeven worden."])

    def _tellTrains(self, game, colors=None):
        if colors is None:
            colors = game.COLORS        
        for color in colors:
            length = game.getTrainLength(color)
            dict = {
                "color": color,
                "length": length}
            if length == 0:
                self._output(["Trein %(color)s heeft nog geen enkele wagon."], dict)
            elif length == 1:
                self._output(["Trein %(color)s heeft 1 wagon."], dict)
            elif length < 5:
                self._output(["Trein %(color)s heeft %(length)i wagons."], dict)
            else:
                self._output(["Trein %(color)s is helemaal compleet."], dict)

    def _tellTurn(self, game):
        self._output(["De beurt is aan %s." % game.getActivePlayer()])

    def _getProperPlayerName(self, game, nick):
        for player in game.getPlayers():
            if nick == player.lower():
                return player
        return nick

    def _getMatchIndices(self, matches):
        indices = ""
        for i in range(len(matches)):
            if matches[i]:
                if indices == "":
                    indices = str(i+1)
                else:
                    indices = indices.replace(" en", ",")
                    indices = indices + " en " + str(i+1)
        return indices

    def _output(self, lines, dict={}):
        for line in lines:
            self._streamer.output(line % dict)

    def _privateOutput(self, nick, line, dict={}):
        self._streamer.privateOutput(nick, line % dict)

class _Command():
    def __init__(self, gameState, isActive, regex, function):
        import re
        self._gameState = gameState
        self._isActive = isActive
        self._regex = regex
        self._pattern = re.compile(regex)
        self._function = function

    def match(self, gameState, isActive, line):
        if isinstance(self._gameState, list):
            if gameState not in self._gameState:
                return False
        else:
            if gameState != self._gameState:
                return False
        if isinstance(self._isActive, list):
            if isActive not in self._isActive:
                return False
        else:
            if isActive != self._isActive:
                return False
        return self._pattern.match(line)

    def function(self, game, nick, dict):
        self._function(game, nick, dict)