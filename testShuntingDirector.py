#!/usr/bin/python
# -*- coding: latin-1 -*-

import unittest
from ShuntingDirector import ShuntingDirector

class GIVEN_a_director(unittest.TestCase):
    def setUp(self):
        self.output = MemoryStreamer()
        self.director = ShuntingDirector(self.output)

    def test_WHEN_you_reorder_35____THEN_the_result_is_3_5_1_2_4(self):
        self.assertEqual(self.director._getIndicesList("35..."), [3,5,1,2,4])

    def test_WHEN_you_reorder_123___THEN_the_result_is_1_2_3_4_5(self):
        self.assertEqual(self.director._getIndicesList("123.."), [1,2,3,4,5])

class GIVEN_a_director_with_no_games_running(unittest.TestCase):
    def setUp(self):
        self.nick1 = "someone"
        self.nick2 = "another"
        self.output = MemoryStreamer()
        self.director = ShuntingDirector(self.output)

    def test_WHEN_a_player_ask_for_the_rules_including_the_name_of_the_game_THEN_they_are_told(self):
        self.director.parse(self.nick2, "Wat zijn de spelregels van Kijfhoek?")
        self.assertTrue(self.output.match(["De spelregels zijn"]))

    def test_WHEN_a_player_ask_for_the_rules_without_the_name_of_the_game_THEN_they_are_not_told(self):
        self.director.parse(self.nick2, "Wat zijn de spelregels?")
        self.assertFalse(self.output.match(["De spelregels zijn"]))

    def test_WHEN_someone_mentions_the_name_of_the_game_THEN_the_director_yields_the_starting_instructions(self):
        self.director.parse(self.nick1, "Een regel waarin Kijfhoek wordt gebruikt.")
        self.assertTrue(self.output.match(["Op de volgende manieren kun je Kijfhoek bijvoorbeeld starten:"]))

    def test_WHEN_one_says_Laten_we_shunting_spelen_THEN_the_director_creates_a_new_game_with_the_nick_as_first_player(self):
        self.director.parse(self.nick1, "Laten we Kijfhoek spelen.")
        self.assertEqual(self.director._getGame(self.nick1).getPlayers()[0], self.nick1)

    def test_WHEN_one_says_Laten_we_shunting_spelen_THEN_the_director_tells_people_how_to_join(self):
        self.director.parse(self.nick1, "Laten we Kijfhoek spelen.")
        self.assertTrue(self.output.match([".*speel mee"]))

    def test_WHEN_one_says_laten_WE_shunting_SPELEN_and_let_the_game_start_THEN_then_it_is_told_that_one_cannot_play_it_on_your_own(self):
        self.director.parse(self.nick1, "laten WE kijfhoek SPELEN.")
        self.director.parse(self.nick1, "We beginnen maar snel.")
        self.assertTrue(self.output.match(["Sorry, voor Kijfhoek zijn minstens 2 spelers nodig."]))

    def test_WHEN_another_says_Ik_doe_mee_met_somenone_THEN_another_is_added_to_the_game(self):
        self.director.parse(self.nick1, "Laten we Kijfhoek spelen.")
        self.director.parse(self.nick2, "Ik doe mee met %s!" % self.nick1)
        self.assertTrue(self.nick2 in self.director._getGame(self.nick1).getPlayers())

    def test_WHEN_the_same_player_says_Ik_doe_mee_met_somenone_THEN_then_he_is_not_added_again(self):
        self.director.parse(self.nick1, "Laten we Kijfhoek spelen.")
        self.director.parse(self.nick1, "Ik doe mee met %s!" % self.nick1)
        self.assertEqual(self.director._getGame(self.nick1).getNumberOfPlayers(), 1)

class GIVEN_a_two_player_game_in_setup_mode(unittest.TestCase):
    def setUp(self):
        self.output = MemoryStreamer()
        self.director = ShuntingDirector(self.output)
        self.nick1 = "someone"
        self.director.parse(self.nick1, "Laten we Kijfhoek spelen.")
        self.nick2 = "another"
        self.director.parse(self.nick2, "Ik doe mee met %s!" % self.nick1)

    def test_WHEN_the_owner_says_We_beginnen_THEN_the_game_starts_and_the_cards_of_players_are_secretly_told_to_all_others(self):
        self.director.parse(self.nick1, "We beginnen.")
        self.assertTrue(self.output.match(["De beurt is aan %s." % self.nick1]))
        self.assertFalse(self.output.privateMatch(self.nick1, ["Het opstelterrein van %s bevat de wagons: " % self.nick1]))
        self.assertTrue(self.output.privateMatch(self.nick1, ["Het opstelterrein van %s bevat de wagons: " % self.nick2]))
        self.assertTrue(self.output.privateMatch(self.nick2, ["Het opstelterrein van %s bevat de wagons: " % self.nick1]))
        self.assertFalse(self.output.privateMatch(self.nick2, ["Het opstelterrein van %s bevat de wagons: " % self.nick2]))

    def test_WHEN_a_player_ask_for_the_rules_THEN_they_are_told(self):
        self.director.parse(self.nick2, "Wat zijn de spelregels?")
        self.assertTrue(self.output.match(["De spelregels zijn"]))

    def test_WHEN_one_says_Laten_we_shunting_spelen_THEN_he_is_reminded_of_the_current_game(self):
        self.director.parse(self.nick1, "Laten we Kijfhoek spelen.")
        self.assertTrue(self.output.match(["Sorry %s, je speelt al een spel met %s en %s!" % (self.nick1, self.nick1, self.nick2)]))

    def test_WHEN_3_other_players_join_THEN_the_game_is_started_automaticly(self):
        self.director.parse("Jaap", "Ik speel mee met %s." % self.nick1)
        self.director.parse("Joop", "Ik speel mee met %s." % self.nick1)
        self.director.parse("Joep", "Ik speel mee met %s." % self.nick1)
        self.assertTrue(self.output.match(["De beurt is aan %s." % self.nick1]))

    def test_WHEN_the_owner_says_stop_THEN_that_is_not_allowed(self):
        self.director.parse(self.nick1, "stop")
        self.assertTrue(self.output.match(["Degene die het spel gestart heeft, mag pas stoppen als de rest dat eerst gedaan heeft."]))

    def test_WHEN_player2_says_stop_THEN_that_is_confirmed_and_there_is_one_player_left(self):
        self.director.parse(self.nick2, "stop")
        self.assertTrue(self.output.match(["Jammer dat je niet meespeelt %s" % self.nick2]))
        self.assertEqual(self.director._getGame(self.nick1).getNumberOfPlayers(), 1)

    def test_WHEN_player2_says_stop_AND_player1_says_stop_THEN_the_game_is_over(self):
        self.director.parse(self.nick2, "stop")
        self.director.parse(self.nick1, "stop")
        self.assertTrue(self.output.match(["OK, dan beëindigen we het spel. En het was nog niet eens begonnen!"]))
        self.assertTrue(self.director._getGame(self.nick1) == None)

class GIVEN_a_just_started_game_with_two_players(unittest.TestCase):
    def setUp(self):
        self.output = MemoryStreamer()
        self.director = ShuntingDirector(self.output)
        self.nick1 = "hans"
        self.director.parse(self.nick1, "Laten we Kijfhoek spelen.")
        self.nick2 = "david"
        self.director.parse(self.nick2, "Ik doe mee met %s!" % self.nick1)
        self.director.parse(self.nick1, "We beginnen.")

    def test_WHEN_player1_says_Ik_leg_1_af_THEN_the_card_is_discarded_and_the_new_cards_are_secretly_told_to_player2(self):
        self.director.parse(self.nick1, "Rangeer wagon 3 weg.")
        self.assertTrue(self.output.privateMatch(self.nick1, ["Het opstelterrein van %s bevat de wagons: " % self.nick2]))
        self.assertTrue(self.output.privateMatch(self.nick2, ["Het opstelterrein van %s bevat de wagons: " % self.nick1, "Het opstelterrein van %s bevat de wagons: " % self.nick1]))
        self.assertTrue(self.output.match(["De beurt is aan %s." % self.nick2]))

    def test_WHEN_player1_says_Orden_kaarten_54321_THEN_his_cards_are_reordered_and_the_cards_are_secretly_told_to_player2_and_its_still_player1s_turn(self):
        self.director.parse(self.nick1, "Orden kaarten 54321")
        self.assertTrue(self.output.privateMatch(self.nick2, ["Het opstelterrein van %s bevat de wagons: " % self.nick1, "Het opstelterrein van %s bevat de wagons: " % self.nick1]))
        self.assertTrue(self.output.match(["De beurt is aan %s." % self.nick1]))

    def test_WHEN_player1_says_Orden_kaarten_54____THEN_his_cards_are_reordered_and_the_cards_are_secretly_told_to_player2_and_its_still_player1s_turn(self):
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

    def test_WHEN_player1_says_Speel_kaart_5_THEN_the_train_or_the_extraLocomotives_are_updated_and_his_new_hand_is_shown_to_others_and_it_is_told_who_is_next(self):
        self.director.parse(self.nick1, "Heuvel wagon 5")
        trainUpdate = self.output.match(["Trein [ROGBP][a-z]+ heeft 1 wagon."])
        extraLocomotivesUpdate = self.output.match(["Er is plek voor nog maar 1 foute wagon op het zijspoor"])
        self.assertTrue(trainUpdate != extraLocomotivesUpdate)
        self.assertTrue(self.output.privateMatch(self.nick2, ["Het opstelterrein van %s bevat de wagons: " % self.nick1, "Het opstelterrein van %s bevat de wagons: " % self.nick1]))
        self.assertTrue(self.output.match(["De beurt is aan %s." % self.nick2]))

    def test_WHEN_player1_says_Hint_David_Blauw_THEN_that_player_is_hinted_and_hints_left_become_7_and_it_is_told_who_is_next(self):
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

    def test_WHEN_player1_says_Hint_Oranje_aan_David_THEN_hints_left_become_7(self):
        self.director.parse(self.nick1, "Hint Oranje aan David")
        self.assertTrue(self.output.match(["Er mogen nog 7 hints"]))

    def test_WHEN_player1_says_Hint_unknown_3_THEN_that_is_not_counted_as_move(self):
        self.director.parse(self.nick1, "Hint Blauw aan unknown")
        self.assertFalse(self.output.match(["De beurt is aan %s." % self.nick2]))

    def test_WHEN_player1_says_Hint_player1_3_THEN_that_is_not_counted_as_move(self):
        self.director.parse(self.nick1, "Hint Blauw aan %s" % self.nick1)
        self.assertFalse(self.output.match(["De beurt is aan %s." % self.nick2]))

    def test_WHEN_player1_says_Hint_blauw_aan_player2_THEN_that_that_is_a_legal_move(self):
        self.director.parse(self.nick1, "Hint Blauw aan %s" % self.nick2)
        self.assertTrue(self.output.match(["De beurt is aan %s." % self.nick2]))

    def test_WHEN_the_9th_hint_is_played_THEN_that_that_is_not_legal_move(self):
        self.director.parse(self.nick1, "Hint Blauw aan %s" % self.nick2)
        self.director.parse(self.nick2, "Hint Blauw aan %s" % self.nick1)
        self.director.parse(self.nick1, "Hint Blauw aan %s" % self.nick2)
        self.director.parse(self.nick2, "Hint Blauw aan %s" % self.nick1)
        self.director.parse(self.nick1, "Hint Blauw aan %s" % self.nick2)
        self.director.parse(self.nick2, "Hint Blauw aan %s" % self.nick1)
        self.director.parse(self.nick1, "Hint Blauw aan %s" % self.nick2)
        self.director.parse(self.nick2, "Hint Blauw aan %s" % self.nick1)
        self.assertTrue(self.output.match(["Er mogen geen hints gegeven worden",
                                        "De beurt is aan %s." % self.nick1]))
        self.director.parse(self.nick1, "Hint Blauw aan %s" % self.nick2)
        self.assertTrue(self.output.match(["Jammer %s, maar er mogen nu geen hints meer gegegeven worden." % self.nick1]))
        self.director.parse(self.nick1, "Rangeer 1 af")
        self.assertTrue(self.output.match(["Jammer", "Er mag", "De beurt is aan %s." % self.nick2]))

    def test_WHEN_player1_says_Hint_David_B_THEN_that_player_is_hinted_and_hints_left_become_7_and_it_is_told_who_is_next(self):
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

    def test_WHEN_a_player_ask_for_the_rules_THEN_they_are_told(self):
        self.director.parse(self.nick2, "Wat zijn de spelregels?")
        self.assertTrue(self.output.match(["De spelregels zijn"]))

    def test_WHEN_a_player_asks_for_help_THEN_it_is_shown(self):
        self.director.parse(self.nick2, "HELP!!!!!")
        self.assertTrue(self.output.match(["De beurt is aan",
                                        "In je beurt heb je drie mogelijkheden:"]))

    def test_WHEN_a_player_ask_for_the_number_of_hints_THEN_that_is_told(self):
        self.director.parse(self.nick2, "Hoeveel hints hebben we nog?")
        self.assertTrue(self.output.match(["Er mogen nog 8 hints gegeven worden."]))

    def test_WHEN_a_player_ask_for_the_number_of_extraLocomotives_THEN_that_is_told(self):
        self.director.parse(self.nick2, "Hoeveel plekken op het zijspoor hebben we nog?")
        self.assertTrue(self.output.match(["Er is nog plek voor 2 foute wagons op het zijspoor"]))

    def test_WHEN_a_player_ask_for_the_trains_THEN_that_is_told(self):
        self.director.parse(self.nick2, "Hoe staan onze treinen er voor?")
        self.assertTrue(self.output.match(["Trein Blauw heeft nog geen enkele wagon."]))

    def test_WHEN_players_play_lots_of_wrong_cards_THEN_the_game_is_over_and_the_score_is_told(self):
        for i in range(5):
            self.director.parse(self.nick1, "Heuvel 1")
            self.director.parse(self.nick2, "Heuvel 1")
        self.assertTrue(self.output.match(["Het spel is afgelopen."]))
        self.assertTrue(self.output.match(["Jullie hebben in totaal [1-9]?[0-9] wagons correct opgesteld."]))

    def test_WHEN_player1_say_stop_THEN_is_not_over_yet(self):
        self.director.parse(self.nick1, "Ik stop er mee!")
        self.director._getGame(self.nick1)

    def test_WHEN_player1_AND_player2_says_stop_THEN_the_game_stops(self):
        self.director.parse(self.nick1, "Ik stop")
        self.director.parse(self.nick2, "Ik ga ook stoppen.")
        self.assertTrue(self.output.match(["OK, iedereen wil het spelletje stoppen"]))
        self.assertEquals(self.director._getGame(self.nick1), None)

    def test_WHEN_player2_AND_player1_says_stop_THEN_the_game_stops(self):
        self.director.parse(self.nick1, "Ik stop")
        self.director.parse(self.nick2, "Ik ga ook stoppen.")
        self.assertTrue(self.output.match(["OK, iedereen wil het spelletje stoppen"]))
        self.assertEquals(self.director._getGame(self.nick1), None)

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
