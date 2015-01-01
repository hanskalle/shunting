#!/usr/bin/python
# -*- coding: latin-1 -*-

import unittest
from ShuntingDirector import ShuntingDirector

#Hmm, what has this behavior to do with being a director?
class New_Director(unittest.TestCase):
    def setUp(self):
        self.output = MemoryStreamer()
        self.director = ShuntingDirector(self.output)

    def test_Reorder_35xxx_Yields_3_5_1_2_4(self):
        self.assertEqual(self.director._getIndicesList("35..."), [3,5,1,2,4])

    def test_Reordering_123xx_Yields_1_2_3_4_5(self):
        self.assertEqual(self.director._getIndicesList("123.."), [1,2,3,4,5])

class Director_with_no_games_running(unittest.TestCase):
    def setUp(self):
        self.nick1 = "someone"
        self.nick2 = "another"
        self.output = MemoryStreamer()
        self.director = ShuntingDirector(self.output)

    def test_After_player_asking_for_Kijfhoek_rules_Rules_do_appear(self):
        self.director.parse(self.nick2, "Wat zijn de spelregels van Kijfhoek?")
        self.assertTrue(self.output.match(["De spelregels zijn"]))

    def test_After_player_asking_for_the_rules_without_name_of_game_Rules_do_not_appear(self):
        self.director.parse(self.nick2, "Wat zijn de spelregels?")
        self.assertFalse(self.output.match(["De spelregels zijn"]))

    def test_After_mentioning_Kijfhoek_Starting_instructions_appear(self):
        self.director.parse(self.nick1, "Een regel waarin Kijfhoek wordt gebruikt.")
        self.assertTrue(self.output.match(["Op de volgende manieren kun je Kijfhoek bijvoorbeeld starten:"]))

    def test_After_parsing_laten_we_shunting_spelen_New_game_has_nick_as_first_and_only_player(self):
        self.director.parse(self.nick1, "Laten we Kijfhoek spelen.")
        self.assertEqual(self.director._getGame(self.nick1).getPlayers()[0], self.nick1)
        self.assertEqual(len(self.director._getGame(self.nick1).getPlayers()), 1)

    def test_After_parsing_Laten_we_shunting_spelen_How_to_join_message_appear(self):
        self.director.parse(self.nick1, "Laten we Kijfhoek spelen.")
        self.assertTrue(self.output.match([".*speel mee"]))
        
class One_player_game_in_setup(unittest.TestCase):
    def setUp(self):
        self.nick1 = "SomeOne"
        self.nick2 = "Another"
        self.output = MemoryStreamer()
        self.director = ShuntingDirector(self.output)
        self.director.parse(self.nick1, "Laten we Kijfhoek spelen.")

    def test_After_parsing_We_beginnen_Message_more_players_needed_appear(self):
        self.director.parse(self.nick1, "We beginnen maar snel!")
        self.assertTrue(self.output.match(["Sorry, voor Kijfhoek zijn minstens 2 spelers nodig"]))

    def test_After_parsing_Nick2_joins_nick1_Nick2_is_added_as_player(self):
        self.director.parse(self.nick2, "Ik doe mee met %s!" % self.nick1)
        self.assertTrue(self.nick2 in self.director._getGame(self.nick1).getPlayers())

    def test_After_parsing_Nick1_joins_nick1_Nick1_is_not_added_again(self):
        self.director.parse(self.nick1, "Ik doe mee met %s!" % self.nick1)
        self.assertEqual(self.director._getGame(self.nick1).getNumberOfPlayers(), 1)

    def test_After_pruning_with_empty_list_Game_is_ended(self):
        self.director.prune([])
        self.assertTrue(self.output.match(["OK, dan beëindigen we het spel."]))

    def test_After_pruning_with_list_with_just_nick2_Game_is_ended(self):
        self.director.prune([self.nick2])
        self.assertTrue(self.output.match(["OK, dan beëindigen we het spel."]))

    def test_After_pruning_with_list_with_just_nick1_and_nick2_Game_is_not_ended(self):
        self.director.prune([self.nick2, self.nick1])
        self.assertFalse(self.output.match(["OK, dan beëindigen we het spel."]))

class Two_player_game_in_setup(unittest.TestCase):
    def setUp(self):
        self.output = MemoryStreamer()
        self.director = ShuntingDirector(self.output)
        self.nick1 = "someone"
        self.director.parse(self.nick1, "Laten we Kijfhoek spelen.")
        self.nick2 = "another"
        self.director.parse(self.nick2, "Ik doe mee met %s!" % self.nick1)

    def test_After_owner_says_We_beginnen_Player1_gets_turn_and_the_cards_of_players_are_told_to_all_others_in_private(self):
        self.director.parse(self.nick1, "We beginnen.")
        self.assertTrue(self.output.match(["De beurt is aan %s." % self.nick1]))
        self.assertFalse(self.output.privateMatch(self.nick1, ["Het opstelterrein van %s bevat de wagons: " % self.nick1]))
        self.assertTrue(self.output.privateMatch(self.nick1, ["Het opstelterrein van %s bevat de wagons: " % self.nick2]))
        self.assertTrue(self.output.privateMatch(self.nick2, ["Het opstelterrein van %s bevat de wagons: " % self.nick1]))
        self.assertFalse(self.output.privateMatch(self.nick2, ["Het opstelterrein van %s bevat de wagons: " % self.nick2]))

    def test_After_parsing_request_for_rule_Rules_appear(self):
        self.director.parse(self.nick2, "Wat zijn de spelregels?")
        self.assertTrue(self.output.match(["De spelregels zijn"]))

    def test_After_parsing_Laten_we_shunting_spelen_Player_is_reminded_of_the_current_game(self):
        self.director.parse(self.nick1, "Laten we Kijfhoek spelen.")
        self.assertTrue(self.output.match(["Sorry %s, je speelt al een spel met %s en %s!" % (self.nick1, self.nick1, self.nick2)]))

    def test_After_3_other_players_joining_Game_is_started_automaticly(self):
        self.director.parse("Jaap", "Ik speel mee met %s." % self.nick1)
        self.director.parse("Joop", "Ik speel mee met %s." % self.nick1)
        self.director.parse("Joep", "Ik speel mee met %s." % self.nick1)
        self.assertTrue(self.output.match(["De beurt is aan %s." % self.nick1]))

    def test_After_owner_says_stop_Not_allowed_message_appears(self):
        self.director.parse(self.nick1, "stop")
        self.assertTrue(self.output.match(["Degene die het spel gestart heeft, mag pas stoppen als de rest dat eerst gedaan heeft."]))

    def test_After_player2_says_stop_Its_confirmed_and_game_has_1_player(self):
        self.director.parse(self.nick2, "stop")
        self.assertTrue(self.output.match(["Jammer dat je niet meespeelt %s" % self.nick2]))
        self.assertEqual(self.director._getGame(self.nick1).getNumberOfPlayers(), 1)

    def test_After_player2_says_stop_and_player1_says_stop_Its_confirmed_and_game_is_over(self):
        self.director.parse(self.nick2, "stop")
        self.director.parse(self.nick1, "stop")
        self.assertTrue(self.output.match(["OK, dan beëindigen we het spel. En het was nog niet eens begonnen!"]))
        self.assertTrue(self.director._getGame(self.nick1) == None)

class Just_started_2_player_game(unittest.TestCase):
    def setUp(self):
        self.output = MemoryStreamer()
        self.director = ShuntingDirector(self.output)
        self.nick1 = "hans"
        self.director.parse(self.nick1, "Laten we Kijfhoek spelen.")
        self.nick2 = "david"
        self.director.parse(self.nick2, "Ik doe mee met %s!" % self.nick1)
        self.director.parse(self.nick1, "We beginnen.")

    def test_After_player1_says_Ik_leg_1_af_New_cards_are_privatly_told_to_player2_only_and_its_player2s_turn(self):
        self.director.parse(self.nick1, "Rangeer wagon 3 weg.")
        self.assertFalse(self.output.privateMatch(self.nick1, ["Het opstelterrein van %s bevat de wagons: " % self.nick1]))
        self.assertTrue(self.output.privateMatch(self.nick2, ["Het opstelterrein van %s bevat de wagons: " % self.nick1, "Het opstelterrein van %s bevat de wagons: " % self.nick1]))
        self.assertTrue(self.output.match(["De beurt is aan %s." % self.nick2]))

    def test_After_player1_says_Orden_wagons_54321_His_cards_are_secretly_told_to_player2_and_its_still_player1s_turn(self):
        self.director.parse(self.nick1, "Orden wagons 54321")
        self.assertTrue(self.output.privateMatch(self.nick2, ["Het opstelterrein van %s bevat de wagons: " % self.nick1, "Het opstelterrein van %s bevat de wagons: " % self.nick1]))
        self.assertTrue(self.output.match(["De beurt is aan %s." % self.nick1]))

    def test_After_player1_says_Orden_54xxx_His_cards_reordered_and_are_secretly_told_to_player2_and_its_still_player1s_turn(self):
        originalOrder = self.director._getGame(self.nick1).getHandCards(self.nick1)
        self.director.parse(self.nick1, "Orden kaarten 54321")
        newOrder = self.director._getGame(self.nick1).getHandCards(self.nick1)
        self.assertNotEqual(originalOrder, newOrder)
        self.assertTrue(self.output.privateMatch(self.nick2, ["Het opstelterrein van %s bevat de wagons: " % self.nick1, "Het opstelterrein van %s bevat de wagons: " % self.nick1]))
        self.director.parse(self.nick1, "Orden kaarten 54321")
        newOrder = self.director._getGame(self.nick1).getHandCards(self.nick1)
        self.assertEqual(originalOrder, newOrder)
        self.director.parse(self.nick1, "Orden kaarten 45...")
        newOrder = self.director._getGame(self.nick1).getHandCards(self.nick1)
        self.assertNotEqual(originalOrder, newOrder)
        self.assertTrue(self.output.privateMatch(self.nick2, ["Het opstelterrein van %s bevat de wagons: " % self.nick1, "Het opstelterrein van %s bevat de wagons: " % self.nick1]))
        self.director.parse(self.nick1, "Orden kaarten 345..")
        newOrder = self.director._getGame(self.nick1).getHandCards(self.nick1)
        self.assertEqual(originalOrder, newOrder)
        self.assertFalse(self.output.match(["De beurt is aan %s." % self.nick2]))

    def test_After_player1_says_Heuvel_wagon_5_Train_or_the_zijspoor_is_updated_and_His_hand_is_shown_to_others_and_it_is_told_who_is_next(self):
        self.director.parse(self.nick1, "Heuvel wagon 5")
        trainUpdate = self.output.match(["Trein [ROGBP][a-z]+ heeft 1 wagon."])
        extraLocomotivesUpdate = self.output.match(["Er is plek voor nog maar 1 foute wagon op het zijspoor"])
        self.assertTrue(trainUpdate != extraLocomotivesUpdate)
        self.assertTrue(self.output.privateMatch(self.nick2, ["Het opstelterrein van %s bevat de wagons: " % self.nick1, "Het opstelterrein van %s bevat de wagons: " % self.nick1]))
        self.assertTrue(self.output.match(["De beurt is aan %s." % self.nick2]))

    def test_After_player1_says_Hint_David_Blauw_Player2_is_hinted_and_hints_left_become_7_and_it_is_told_who_is_next(self):
        self.director.parse(self.nick1, "Hint David: Blauw")
        hintCount = 0
        if self.output.match(["%s heeft geen B-en" % self.nick2]):
            hintCount += 1
        if self.output.match(["Wagon [1-5] van %s is een B." % self.nick2]):
            hintCount += 1
        if self.output.match(["De wagons [1-5](, [1-5])* en [1-5] van %s zijn B-en." % self.nick2]):
            hintCount += 1
        self.assertEqual(hintCount, 1)
        self.assertTrue(self.output.match(["Er mogen nog 7 hints"]))
        self.assertTrue(self.output.match(["De beurt is aan %s." % self.nick2]))

    def test_After_player1_says_Hint_Oranje_aan_David_Hints_left_become_7(self):
        self.director.parse(self.nick1, "Hint Oranje aan David")
        self.assertTrue(self.output.match(["Er mogen nog 7 hints"]))

    def test_After_player1_says_Hint_unknown_3_It_is_ignored(self):
        self.director.parse(self.nick1, "Hint Blauw aan unknown")
        self.assertFalse(self.output.match(["De beurt is aan %s." % self.nick2]))

    def test_After_player1_says_Hint_blauw_aan_player2_Its_players2_turn(self):
        self.director.parse(self.nick1, "Hint Blauw aan %s" % self.nick2)
        self.assertTrue(self.output.match(["De beurt is aan %s." % self.nick2]))

    def test_After_hinting_for_the_9th_time_It_is_told_there_aro_no_hints_left(self):
        self.director.parse(self.nick1, "Hint Blauw aan %s" % self.nick2)
        self.director.parse(self.nick2, "Hint Blauw aan %s" % self.nick1)
        self.director.parse(self.nick1, "Hint Blauw aan %s" % self.nick2)
        self.director.parse(self.nick2, "Hint Blauw aan %s" % self.nick1)
        self.director.parse(self.nick1, "Hint Blauw aan %s" % self.nick2)
        self.director.parse(self.nick2, "Hint Blauw aan %s" % self.nick1)
        self.director.parse(self.nick1, "Hint Blauw aan %s" % self.nick2)
        self.director.parse(self.nick2, "Hint Blauw aan %s" % self.nick1)
        self.assertFalse(self.output.match(["Jammer %s, maar er mogen nu geen hints meer gegegeven worden." % self.nick1]))
        self.director.parse(self.nick1, "Hint Blauw aan %s" % self.nick2)
        self.assertTrue(self.output.match(["Jammer %s, maar er mogen nu geen hints meer gegegeven worden." % self.nick1]))

    def test_After_player1_says_Hint_David_3_Player_is_hinted_and_hints_left_become_7_and_it_is_told_who_is_next(self):
        self.director.parse(self.nick1, "Hint speler David het prachtige getal van de eenheid: 3")
        hintCount = 0
        if self.output.match(["%s heeft geen 3-en." % self.nick2]):
            hintCount += 1
        if self.output.match(["Wagon [1-5] van %s is een 3." % self.nick2]):
            hintCount += 1
        if self.output.match(["De wagons [1-5](, [1-5])* en [1-5] van %s zijn 3-en." % self.nick2]):
            hintCount += 1
        self.assertEqual(hintCount, 1)
        self.assertTrue(self.output.match(["Er mogen nog 7 hints"]))
        self.assertTrue(self.output.match(["De beurt is aan %s." % self.nick2]))

    def test_After_request_for_rules_Rules_appear(self):
        self.director.parse(self.nick2, "Wat zijn de spelregels?")
        self.assertTrue(self.output.match(["De spelregels zijn"]))

    def test_After_request_for_help_Help_appears(self):
        self.director.parse(self.nick2, "HELP!!!!!")
        self.assertTrue(self.output.match(["De beurt is aan",
                                        "In je beurt heb je drie mogelijkheden:"]))

    def test_After_request_for_number_of_hints_Hints_left_appear(self):
        self.director.parse(self.nick2, "Hoeveel hints hebben we nog?")
        self.assertTrue(self.output.match(["Er mogen nog 8 hints gegeven worden."]))

    def test_After_request_for_room_on_zijspoor_Zijspoor_room_appears(self):
        self.director.parse(self.nick2, "Hoeveel plekken op het zijspoor hebben we nog?")
        self.assertTrue(self.output.match(["Er is nog plek voor 2 foute wagons op het zijspoor"]))

    def test_After_request_for_cards_in_deck_Number_appear(self):
        self.director.parse(self.nick2, "Hoeveel wagons staan er nog op het wachtspoor?")
        self.assertTrue(self.output.match(["Op het wachtspoor staan nog 40 wagons gereed om te verwerken."]))

    def test_After_request_for_trains_Trains_appear(self):
        self.director.parse(self.nick2, "Hoe staan onze treinen er voor?")
        self.assertTrue(self.output.match(["Trein Rood heeft nog geen enkele wagon."]))
        self.assertTrue(self.output.match(["Trein Blauw heeft nog geen enkele wagon."]))

    def test_After_playing_lots_of_wrong_cards_Game_is_over_and_score_appears(self):
        for i in range(5):
            self.director.parse(self.nick1, "Heuvel 1")
            self.director.parse(self.nick2, "Heuvel 1")
        self.assertTrue(self.output.match(["Het spel is afgelopen."]))
        self.assertTrue(self.output.match(["Jullie hebben in totaal [1-9]?[0-9] wagons correct opgesteld."]))

    def test_After_player1_say_stop_Games_is_still_there(self):
        self.director.parse(self.nick1, "Ik stop er mee!")
        self.director._getGame(self.nick1)

    def test_After_player1_and_player2_says_stop_Stopping_is_confirmed_and_game_is_gone(self):
        self.director.parse(self.nick1, "Ik stop")
        self.director.parse(self.nick2, "Ik ga ook stoppen.")
        self.assertTrue(self.output.match(["OK, iedereen wil het spelletje stoppen"]))
        self.assertEquals(self.director._getGame(self.nick1), None)

    def test_After_player2_and_player1_says_stop_Stopping_is_confirmed_and_game_is_gone(self):
        self.director.parse(self.nick1, "Ik stop")
        self.director.parse(self.nick2, "Ik ga ook stoppen.")
        self.assertTrue(self.output.match(["OK, iedereen wil het spelletje stoppen"]))
        self.assertEquals(self.director._getGame(self.nick1), None)

    def test_After_pruning_with_empty_list_Game_is_ended(self):
        self.director.prune([])
        self.assertTrue(self.output.match(["OK, iedereen wil het spelletje stoppen"]))

    def test_After_pruning_with_empty_list_Score_appears(self):
        self.director.prune([])
        self.assertTrue(self.output.match(["Jullie hebben in totaal [1-9]?[0-9] wagons correct opgesteld."]))

class MemoryStreamer():
    def __init__(self):
        self._lines = []
        self._private = {}

    def output(self, line):
        self._lines.append(line)

    def dump(self):
        for line in self._lines:
            print line

    def privateOutput(self, nick, line):
        if not nick in self._private:
            self._private[nick] = []
        self._private[nick].append(line)

    def privateDump(self, nick):
        if nick in self._private:
            for line in self._private[nick]:
                print line

    def privateMatch(self, nick, expressions):
        matchFound = False
        if nick in self._private:
            lines = self._private[nick]
            import re
            patterns = []
            for expression in expressions:
                patterns.append(re.compile(expression))
            for i in range(len(lines)-len(patterns)+1):
                matchFound = True
                for j in range(len(patterns)):
                    if not patterns[j].match(lines[i+j]):
                        matchFound = False
                        break
                if matchFound:
                    break
        return matchFound

    def match(self, expressions):
        import re
        patterns = []
        for expression in expressions:
            patterns.append(re.compile(expression))
        matchFound = False
        for i in range(len(self._lines)-len(patterns)+1):
            matchFound = True
            for j in range(len(patterns)):
                if not patterns[j].match(self._lines[i+j]):
                    matchFound = False
                    break
            if matchFound:
                break
        return matchFound

if __name__ == '__main__':
    unittest.main()
