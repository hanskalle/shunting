#!/usr/bin/python
# -*- coding: latin-1 -*-
__module_name__ = "ShuntingDirector"
__module_version__ = "1.2"
__module_description__ = "Shunting game director voor Kijfhoek."

from HanabiGame import HanabiGame

class ShuntingDirector():
    NAME = "Kijfhoek"
    COLORMAP = {
            "R": "Rood",
            "O": "Oranje",
            "G": "Groen",
            "B": "Blauw",
            "P": "Paars"
        }

    def __init__(self, streamer):
       self._streamer = streamer
       self._games = []
       self._knowledge = {}
       self._initCommands()
       self._stoppers = set([])

    def _initCommands(self):
        self._commands = [
            _Command(None, False, "(.* )?" + self.NAME.lower() + " (.* )?spelen(.*[^?])?$", self._createNewGame),
            _Command(None, False, ".*regels( .*)? " + self.NAME.lower() + ".*\?$", self._showRules),
            _Command(None, False, ".*" + self.NAME.lower(), self._showStartingInstructions),
            _Command(None, False, ".*(doe|speel) (.* )?mee[, ](.* )?(?P<owner>[A-Za-z_\-0-9]+)", self._joinGame),
            _Command(HanabiGame.SETUP, False, ".*we (.* )?beginnen(.*[^?])?$", self._startGame),
            _Command(HanabiGame.SETUP, False, ".*stop(.*[^?])?$", self._leaveGame),
            _Command(HanabiGame.ON, True, ".*(dump|verwijder)( [^1-5]*)? (?P<index>[1-5])(ste|de|e)?( [^1-5]*)?[\.\!]?$", self._discard),
            _Command(HanabiGame.ON, True, ".*(koppel|heuvel)( [^1-5]*)? (?P<index>[1-5])(ste|de|e)?( [^1-5]*)?( aan)?( [^1-5]*)?[\.\!]?$", self._play),
            _Command(HanabiGame.ON, True, ".*hint (.+ )?((cijfer|getal) )?(.+ )?(?P<hint>[1-5]) (aan|voor) (speler )?(?P<player>[A-Za-z_\-0-9]+)", self._hint),
            _Command(HanabiGame.ON, True, ".*hint (.+ )?(kleur )?(.+ )?(?P<hint>[rogbp])(ood|ranje|roen|lauw|aars)? (aan|voor) (speler )?(?P<player>[A-Za-z_\-0-9]+)", self._hint),
            _Command(HanabiGame.ON, True, ".*hint (speler )?(?P<player>[A-Za-z_\-0-9]+)(: ?| )?(.+ )?((cijfer|getal) )?(.+ )?(?P<hint>[1-5])", self._hint),
            _Command(HanabiGame.ON, True, ".*hint (speler )?(?P<player>[A-Za-z_\-0-9]+)(: ?| )?(.+ )?(kleur )?(.+ )?(?P<hint>[rogbp])", self._hint),
            _Command(HanabiGame.ON, [True, False], "(help|hulp|om hulp)(!+|.)$", self._showHelp),
            _Command(HanabiGame.ON, [True, False], ".*(orden|(her|rang)?schik) (.* )?(?P<order>[1-5]{1,5}\.{0,4})( .*)?", self._reorder),
            _Command(HanabiGame.ON, [True, False], ".*stop(.*[^?])?$", self._stopGame),
            _Command(HanabiGame.ON, [True, False], ".*opstelterrein.*\?$", self._showYards),
            _Command([HanabiGame.SETUP, HanabiGame.ON], [True, False], "(.* )?" + self.NAME.lower() + " spelen.*[^?]$", self._stillPlayingAnotherGame),
            _Command([HanabiGame.SETUP, HanabiGame.ON], [True, False], ".*ik (.* )?mee ((.+|met) )?(?P<owner>[A-Za-z_\-0-9]+)", self._stillPlayingAnotherGame),
            _Command([HanabiGame.SETUP, HanabiGame.ON], [True, False], ".*hints.*\?$", self._showHints),
            _Command([HanabiGame.SETUP, HanabiGame.ON], [True, False], ".*zijspoor.*\?$", self._showSiding),
            _Command([HanabiGame.SETUP, HanabiGame.ON], [True, False], ".*wachtspoor.*\?$", self._showWaitingTrack),
            _Command([HanabiGame.SETUP, HanabiGame.ON], [True, False], ".*treinen.*\?$", self._showTrains),
            _Command([HanabiGame.SETUP, HanabiGame.ON], [True, False], ".*kennis.*\?$", self._tellKnowledge),
            _Command([HanabiGame.SETUP, HanabiGame.ON], [True, False], ".*regels.*\?$", self._showRules)]

    def parse(self, nick, line):
        line = line.lower()
        game = self._getGame(nick)
        gameState = self._getGameState(game)
        isActivePlayer = self._isActivePlayer(game, nick)
        for command in self._commands:
            match = command.match(gameState, isActivePlayer , line)
            if match:
                dict = match.groupdict()
                dict["nick"] = nick
                command.function(game, nick, dict)
                break
                
    def prune(self, activeNicks):
        for game in self._games:
            for player in game.getPlayers():
                if not player in activeNicks:
                    self.quit(player)

    def quit(self, nick):
        game = self._getGame(nick)
        self._output(["Helaas, %s is er vandoor. Ik tel het maar als stopper." % nick])
        dict = {"nick": nick}
        if game.isSettingUp():
            self._leaveGame(game, nick, dict)
        else:
            self._stopGame(game, nick, dict)

    def _getGameState(self, game):
        if game:
            return game.getState()
        else:
            return None

    def _isActivePlayer(self, game, nick):
        if game:
            return nick == game.getActivePlayer()
        else:
            return False

    def _getGame(self, nick):
        gameFound = None
        nick = nick.lower()
        for game in self._games:
            for player in game.getPlayers():
                if nick == player.lower():
                    gameFound = game
                    break
        return gameFound

    def _getMaxLengthPlayers(self, game):
        maxLength = 0
        for player in game.getPlayers():
            length = len(player)
            if length > maxLength:
                maxLength = length
        return maxLength

    def _getNamelist(self, players):
        players = list(players)
        namestring = ""
        if len(players) > 0:
            namestring += str(players[0])
        for player in players[1:-1]:
            namestring += ", " + str(player)
        if len(players) > 1:
            namestring += " en " + str(players[-1])
        return namestring

    def _getIndicesList(self, indicesString):
        maxIndex = len(indicesString)
        restIndices = range(1, maxIndex+1)
        indicesList = []
        indicesString = indicesString.replace(".","")
        for index in indicesString:
            index = int(index)
            if index in indicesList:
                return []
            if index <= maxIndex:
                indicesList.append(index)
                restIndices[index-1] = None
        for index in restIndices:
            if not index is None:
                indicesList.append(index)
        return indicesList

    def _getMatchIndices(self, matches):
        indices = []
        for i in range(len(matches)):
            if matches[i]:
                indices.append(i+1)
        return indices

    def _getPropertyDescription(self, property):
        if property in self.COLORMAP:
            return self.COLORMAP[property]
        else:
            return property

    def _getProperPlayerName(self, game, nick):
        for player in game.getPlayers():
            if nick == player.lower():
                return player
        return nick

    def _output(self, lines, dict={}):
        for line in lines:
            self._streamer.output(line % dict)

    def _privateOutput(self, nick, line, dict={}):
        self._streamer.privateOutput(nick, line % dict)
        
    def _initKnowledge(self, game, nick):
        self._knowledge[nick] = []
        for card in game.getHandCards(nick):
            self._knowledge[nick].append("..")

    def _reorderKnowledge(self, nick, indices):
        original = self._knowledge[nick]
        self._knowledge[nick] = []
        for index in indices:
            self._knowledge[nick].append(original[index-1])

    def _setKnowledge(self, nick, indices, data):
        for index in indices:
            if data == "..":
                self._knowledge[nick][index-1] = ".."
            elif data in "12345":
                self._knowledge[nick][index-1] = self._knowledge[nick][index-1][:1] + data
            else:
                self._knowledge[nick][index-1] = data + self._knowledge[nick][index-1][-1:]

    def _tellKnowledge(self, game, nick, dict):
        self._output(["Kennis:"])
        maxLength = self._getMaxLengthPlayers(game)
        for player in game.getPlayers():
            self._output(["%s: %s" % (player.rjust(maxLength+2), "  ".join(self._knowledge[player]))])

    def _createNewGame(self, game, nick, dict):
        game = HanabiGame(nick)
        self._games.append(game)
        self._output(["Nou, %(nick)s, leuk dat je " + self.NAME + " wil spelen."], dict)
        self._tellJoinOrStart(game, dict)

    def _joinGame(self, game, nick, dict):
        game = self._getGame(dict["owner"])
        if game:
            if not nick in game.getPlayers():
                game.addPlayer(nick)
                self._output(["Hoi %(nick)s, leuk dat je meedoet met het " + self.NAME + "-spel van %(owner)s."], dict)
                self._tellJoinOrStart(game, dict)
        else:
            self._output(["Sorry %(nick)s, maar er is geen spel dat gestart is door %(owner)s."], dict)

    def _leaveGame(self, game, nick, dict):
        if nick == game.getOwner():
            if game.getNumberOfPlayers() == 1:
                self._output(["OK, dan be�indigen we het spel. En het was nog niet eens begonnen!"])
                self._removeGame(game)
            else:                
                self._output(["Degene die het spel gestart heeft, mag pas stoppen als de rest dat eerst gedaan heeft."])
        else:
            game.removePlayer(nick)
            self._output(["Jammer dat je niet meespeelt %(nick)s. Aan de andere kant speelt het wel beter met alleen maar intelligente teamleden."], dict)
            self._tellJoinOrStart(game, dict)

    def _stillPlayingAnotherGame(self, game, nick, dict):
        players = self._getNamelist(game.getPlayers())
        dict["players"] = players
        self._output(["Sorry %(nick)s, je speelt al een spel met %(players)s!"], dict)

    def _startGame(self, game, nick, dict):
        owner = game.getOwner()
        if nick == owner:
            if len(game.getPlayers()) > 1:
                game.start()
                self._output(["Ik vertel de wagons op de opstelterreinen via prive-berichten, zodat je als rangeerder niet weet welke wagons er op jouw opstelterrein staan. Let dus op het aparte venster."], dict)
                for player in game.getPlayers():
                    self._initKnowledge(game, player)
                    self._tellHandToOthers(game, player)
                self._tellSiding(game)
                self._tellHints(game)
                self._showHelp(game, nick, dict)
                self._tellTurn(game)
            else:
                self._output(["Sorry, voor Kijfhoek zijn minstens 2 spelers nodig."])
        else:
            dict["owner"] = owner
            self._output(["Sorry %(nick)s, alleen %(owner)s mag een spel laten beginnen."], dict)

    def _discard(self, game, nick, dict):
        self._stoppers.discard(nick)
        index = int(dict["index"])
        game.discard(index)
        self._setKnowledge(nick, [index], "..")
        if game.isOn():
            self._tellHandToOthers(game, nick)
            self._tellHints(game)
        self._nextTurn(game)

    def _play(self, game, nick, dict):
        self._stoppers.discard(nick)
        index = int(dict["index"])
        card = game.getHandCards(nick)[index-1]
        dict["card"] = card
        self._output(["Wagon %(index)s van %(nick)s is een %(card)s."], dict)
        self._setKnowledge(nick, [index], "..")
        if game.play(index):
            color = game.getCardColor(card)
            self._tellTrains(game, color)
            if game.getFireworkLength(color) == 5:
                self._tellHints(game)
        else:
            self._output(["Die belandt op het zijspoor omdat die aan geen enkele trein gekoppeld kan worden."], dict)
            self._tellSiding(game)
        if game.isOn():
            self._tellHandToOthers(game, nick)
        self._nextTurn(game)

    def _hint(self, game, nick, dict):
        self._stoppers.discard(nick)
        if game.getHintsLeft() > 0:
            hint = dict["hint"].upper()
            player = self._getProperPlayerName(game, dict["player"])
            if player != nick:
                if player in game.getPlayers():
                    matches = game.hint(player, hint)
                    indices = self._getMatchIndices(matches)
                    self._setKnowledge(player, indices, hint)
                    dict["indices"] = self._getNamelist(indices)
                    dict["player"] = player
                    dict["hint"] = hint
                    if len(indices) == 0:
                        self._output(["%(player)s heeft geen %(hint)s-en."], dict)
                    elif len(indices) == 1:
                        self._output(["Wagon %(indices)s van %(player)s is een %(hint)s."], dict)
                    else:
                        self._output(["De wagons %(indices)s van %(player)s zijn %(hint)s-en."], dict)
                    self._tellHints(game)
                    self._nextTurn(game)
                else:
                    dict["players"] = self._getNamelist(game.getPlayers())
                    self._output(["Sorry %(nick)s, er is geen speler die %(player)s heet. Probeer opnieuw en kies uit %(players)s."], dict)
            else:
                 self._output(["Jammer %(nick)s, maar jezelf hinten is niet toegestaan. Probeer opnieuw."], dict)
        else:
            self._output(["Jammer %(nick)s, maar er mogen nu geen hints meer gegegeven worden. Pas na het afrangeren van een wagon mag dat weer. Probeer opnieuw."], dict)

    def _nextTurn(self, game):
        if game.isOn():
            self._tellTurn(game)
        else:
            self._tellGameOver(game)
            self._removeGame(game)

    def _reorder(self, game, nick, dict):
        self._stoppers.discard(nick)
        count = game.getMaxHandCards()
        order = dict["order"]
        if len(order) == count:
            order = self._getIndicesList(order)
        if len(order) == count:
            game.reorderHandCards(nick, order)
            self._reorderKnowledge(nick, order)
            self._output(["De wagons van %(nick)s zijn opnieuw gerangschikt."], dict)
            self._tellHandToOthers(game, nick)
        else:
            dict["order"] = "54321"[-count:]
            self._output(["De opgegeven ordening klopt niet. Voor een omgekeerde volgorde geeft je bijvoorbeeld %(order)s op."], dict)

    def _stopGame(self, game, nick, dict):
        self._stoppers.add(nick)
        players = set(game.getPlayers())
        stoppingPlayers = players & self._stoppers
        lastPlayers = players - self._stoppers
        if len(lastPlayers) == 0:
            self._output(["OK, iedereen wil het spelletje stoppen. Jammer, maar helaas..."])
            self._tellGameOver(game)
            self._removeGame(game)
        else:
            dict["stoppingPlayers"] = self._getNamelist(stoppingPlayers)
            dict["lastPlayers"] = self._getNamelist(lastPlayers)
            self._output(["De spelers die het spel willen stoppen: %(stoppingPlayers)s",
                        "Om het spel daadwerkelijk te be�indigen, moeten ook de overigen aangeven dat ze willen stoppen.",
                        "Dat zijn dus: %(lastPlayers)s.",
                        "Zolang nog niet iedereen gestopt is, kunnen de anderen besluiten het spel toch af te maken door weer gewoon mee te spelen."], dict)

    def _showStartingInstructions(self, game, nick, dict):
        self._output([
            "Ik ben een bot die het spelletje " + self.NAME + " kan faciliteren!",
            "Op de volgende manieren kun je " + self.NAME + " bijvoorbeeld starten:",
            "  Laten we " + self.NAME + " spelen.",
            "  Ik wil graag " + self.NAME + " spelen.",
            "Maar je kunt ook eerst vragen om de spelregels van " + self.NAME + "."])

    def _showHelp(self, game, nick, dict):
        length = game.getMaxHandCards()
        self._output([
            "In je beurt heb je drie mogelijkheden:",
            "1) Koppel wagon <index> aan. Bijvoorbeeld: Koppel wagon 2 aan. Of: Ik heuvel nu 2.",
            "2) Verwijder wagon <index>. Bijvoorbeeld: Verwijder wagon 2. Of: Ik dump graag nummer 4.",
            "3) Hint <kleur/cijfer> aan <nick>. Bijvoorbeeld: Hint rood aan David. Of: Hint David: 3",
            "In en buiten je beurt kun je allerlei informatie opvragen. Vraag bijvoorbeeld: Hoeveel hints zijn er nog beschikbaar?",
            "Denk ook aan: wachtspoor, opstelterreinen, zijspoor, treinen, gedeelde kennise en spelregels.",
            "Verder kun je de wagons op je opstelterrein ordenen: Herschik opstelterrein %s." % "34125"[-length:],
            "Tot slot, maar dat is een beetje flauw, kun je aangeven dat je stopt met het spel.",
            "En als je het allemaal niet meer weet, roep je maar om hulp."])

    def _showRules(self, game, nick, dict):
        self._output(["De spelregels zijn erg eenvoudig.",
            "CONTEXT: Op Kijfhoek is het een drukte van belang. Van alle wagons die aankomen moeten verschillende treinen worden samengesteld. Iedere trein heeft een eigen kleur en de wagons moeten in de juiste volgorde worden aangekoppeld. Samen met je collega rangeerders heb je maar ��n nacht om de treinen op orde te krijgen!",
            "DOEL: De rangeerders bouwen samen vijf goederentreinen in de kleuren van de vervoerders: R(ood), O(ranje), G(roen), B(lauw) en P(aars). Elke trein krijgt 5 wagons, genummerd 1 tot en met 5. Probeer samen de treinen zo compleet mogelijk te maken.",
            "VERLOOP: Om beurten rangeer je wagons en geef je elkaar hints. Iedere speler beschikt over een eigen opstelterrein met een aantal wagons. Maar let op: alleen de andere spelers krijgen te zien welke dat zijn. Je hebt dus de hints van anderen nodig om te weten wat je met je wagons moet doen. Zodra er een plaats vrijkomt op je opstelterrein, wordt daar vanaf het wachtspoor een wagon op geplaatst.",
            "BEURT: Tijdens je beurt kies je uit drie mogelijkheden:",
            "1) Geef een hint aan een medespeler. Kies een kleur of een getal en vertel je medespeler welke van zijn of haar wagons daaraan voldoen. Maar let op: je hebt initieel maar 8 hints beschikbaar.",
            "2) Rangeer een wagon weg, deze komt niet meer terug in het spel. De lege plek op je opstelterrein wordt ingenomen door een wagon van het wachtspoor. En als er minder dan 8 hints over zijn, komt er weer een hint bij.",
            "3) Heuvel een wagon om hem te koppelen aan een van de treinen. De kleur moet kloppen en de nummers van de wagons moeten netjes oplopen. Maak je een trein compleet en resten er minder dan 8 hints, komt er weer een hint bij. Maar kan de wagon niet worden gekoppeld aan ��n van de treinen, dan beland die op het zijspoor. In alle gevallen wordt de lege plek op je opstelterrein weer ingenomen door een wagon van het wachtspoor. ",
            "EINDE: Het spel eindigt als:",
            "a) Jullie alle treinen compleet hebben (wauw!).",
            "b) Een derde wagon op het zijspoor terechtkomt. Omdat daar maar plaats voor twee wagons is, blokkeert de derde het hoofdspoor.",
            "c) Nadat de laatste wagon van het wachtspoor gerangeerd is:  dan krijgt iedereen, inclusief de rangeerder die de laatste wagon kreeg, nog 1 beurt.",
            "SCORE: De score is het totaal aantal wagons in de opgebouwde treinen.",
            "NOTA BENE: Er zijn van elke kleur drie wagons met het cijfer 1, twee met 2, 3 en 4 en slechts een enkele met een 5."], dict)

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

    def _showSiding(self, game, nick, dict):
        if game.isOn():
            self._tellSiding(game)
        else:
            self._output(["Initieel is er plek voor 2 foute wagons op het zijspoor. Bij de derde foute wagon raakt het heuvelspoor geblokeerd en is het spel voorbij. Maar op dit moment is het spel nog niet begonnen."], dict)

    def _showWaitingTrack(self, game, nick, dict):
        if game.isOn():
            self._tellWaitingTrack(game)
        else:
            self._output(["Initieel staan er 50 wagons op het wachtspoor. Maar als het spel begint worden de opstelterreinen van de spelers nog gevuld met elk 5 wagons."], dict)

    def _showYards(self, game, nick, dict):
        self._tellYards(game, nick)

    def _removeGame(self, game):
        for player in game.getPlayers():
            self._stoppers.discard(player)
        self._games.remove(game)

    def _tellGameOver(self, game):
        self._output(["Het spel is afgelopen."])
        self._tellTrains(game)
        score = game.getScore()
        self._output(["Jullie hebben in totaal %i wagons correct opgesteld." % score])
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

    def _tellJoinOrStart(self, game, dict):
        dict["owner"] = game.getOwner()
        dict["number_of_players"] = game.getNumberOfPlayers()
        dict["players"] = self._getNamelist(game.getPlayers())
        self._output(["We hebben nu %(number_of_players)i rangeerders: %(players)s."], dict)
        if game.getNumberOfPlayers() == 1:
            self._output(["Wie doet er mee? Er is minimaal nog een tweede rangeerder nodig.",
                    "Zeg 'Ik speel mee met %(owner)s.'."], dict)
        elif game.getNumberOfPlayers() < 5:
            self._output(["%(owner)s, zeg jij wanneer we beginnen?"], dict)
        else:
            self._output(["We hebben nu het maximale aantal bereikt. We beginnen!"])
            self._startGame(game, game.getOwner(), dict)

    def _tellHandToOthers(self, game, nick):
        hand = game.getHandCards(nick)
        if len(hand) > 0:
            hand = "  ".join(hand)
            for another in game.getPlayers():
                if another != nick:
                    self._privateOutput(another, "Het opstelterrein van %s bevat de wagons: %s." % (nick, hand))
        else:
            for another in game.getPlayers():
                if another != nick:
                    self._privateOutput(another, "Het opstelterrein van %s doet er niet meer toe." % nick)

    def _tellSiding(self, game):
        count = game.getThunderstormsLeft()-1
        if count > 1:
            self._output(["Het zijspoor kan nog %i foute wagons opvangen." % count])
        elif count == 1:
            self._output(["Het zijspoor kan nog maar 1 foute wagon opvangen."])
        elif count == 0:
            self._output(["Er is geen plek meer op het zijspoor om foute wagons op te vangen. Bij de volgende foute wagon eindigt het spel!"])
        else:
            self._output(["Het zijspoor was al vol. De laatste foute wagon blokkeert nu het heuvelspoor naar de treinen. Het spel is afgelopen!"])

    def _tellWaitingTrack(self, game):
        count = game.getNumberOfCardsInDeck()
        if count > 1:
            self._output(["Op het wachtspoor staan nog %i wagons gereed om te verwerken." % count])
        elif count == 1:
            self._output(["Op het wachtspoor staat nog maar 1 wagon gereed om te verwerken."])
        else:
            self._output(["Het wachtspoor is leeg. Er zijn geen nieuwe wagons meer. We spelen de laatste ronde."])

    def _tellYards(self, game, nick):
        self._privateOutput(nick, "Zo zien de opstelterreinen er nu uit:")
        maxLength = self._getMaxLengthPlayers(game)
        for player in game.getPlayers():
            if player != nick:
                hand = game.getHandCards(player)
                if len(hand) > 0:
                    hand = ",".join(hand)
                    self._privateOutput(nick, "%s: %s" % (player.rjust(maxLength+2), hand))
                else:
                    self._privateOutput(nick, "%s: doet er niet meer toe." % player.rjust(maxLength+2))

    def _tellHints(self, game):
        if game.getHintsLeft() > 1:
            self._output(["Er mogen nog %i hints gegeven worden." % game.getHintsLeft()])
        elif game.getHintsLeft() == 1:
            self._output(["Er mag nog 1 hint gegeven worden."])
        else:
            self._output(["Er mogen geen hints gegeven worden. Rangeer een wagon af om weer een hint te mogen geven."])

    def _tellTrains(self, game, colors=None):
        if colors is None:
            colors = game.COLORS        
        for color in colors:
            length = game.getFireworkLength(color)
            dict = {
                "color": self._getPropertyDescription(color),
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
        if game.isLastRound():
            self._output(["Let op: dit is de laatste ronde omdat er geen wagons meer op het wachtspoor staan!"])

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
