#!/usr/bin/python

import unittest
from ShuntingDirector import ShuntingDirector

class GIVEN_a_director_with_no_games_running(unittest.TestCase):
    def setUp(self):
        self.nick1 = "someone"
        self.nick2 = "another"
        self.output = MemoryStreamer()
        self.director = ShuntingDirector(self.output)

    def test_WHEN_a_player_ask_for_the_rules_including_the_name_of_the_game_THEN_they_are_told(self):
        self.director.parse(self.nick2, "Wat zijn de spelregels van shunting?")
        self.assertTrue(self.output.match(["De spelregels zijn"]))

    def test_WHEN_a_player_ask_for_the_rules_without_the_name_of_the_game_THEN_they_are_not_told(self):
        self.director.parse(self.nick2, "Wat zijn de spelregels?")
        self.assertFalse(self.output.match(["De spelregels zijn"]))

    def test_WHEN_someone_mentions_the_name_of_the_game_THEN_the_director_yields_the_starting_instructions(self):
        self.director.parse(self.nick1, "Een regel waarin shunting wordt gebruikt.")
        self.assertTrue(self.output.match(["Op de volgende manieren kun je shunting bijvoorbeeld starten:"]))

    def test_WHEN_one_says_Laten_we_shunting_spelen_THEN_the_director_creates_a_new_game_with_the_nick_as_first_player(self):
        self.director.parse(self.nick1, "Laten we shunting spelen.")
        self.assertEqual(self.director._getGame(self.nick1).getPlayers()[0], self.nick1)

    def test_WHEN_one_says_laten_WE_shunting_SPELEN_THEN_the_director_creates_a_new_game_with_the_nick_as_first_player(self):
        self.director.parse(self.nick1, "laten WE shunting SPELEN.")
        self.assertEqual(self.director._getGame(self.nick1).getPlayers()[0], self.nick1)

    def test_WHEN_another_says_Ik_doe_mee_met_somenone_THEN_another_is_added_to_the_game(self):
        self.director.parse(self.nick1, "Laten we shunting spelen.")
        self.director.parse(self.nick2, "Ik doe mee met %s!" % self.nick1)
        self.assertTrue(self.nick2 in self.director._getGame(self.nick1).getPlayers())

    def test_WHEN_the_same_player_says_Ik_doe_mee_met_somenone_THEN_then_he_is_not_added_again(self):
        self.director.parse(self.nick1, "Laten we shunting spelen.")
        self.director.parse(self.nick1, "Ik doe mee met %s!" % self.nick1)
        self.assertEqual(len(self.director._getGame(self.nick1).getPlayers()), 1)

class GIVEN_a_two_player_game_in_setup_mode(unittest.TestCase):
    def setUp(self):
        self.output = MemoryStreamer()
        self.director = ShuntingDirector(self.output)
        self.nick1 = "someone"
        self.director.parse(self.nick1, "Laten we shunting spelen.")
        self.nick2 = "another"
        self.director.parse(self.nick2, "Ik doe mee met %s!" % self.nick1)

    def test_WHEN_the_owner_says_We_beginnen_THEN_the_game_starts_and_the_cards_of_players_are_secretly_told_to_all_others(self):
        self.director.parse(self.nick1, "We beginnen.")
        self.assertFalse(self.output.privateMatch(self.nick1, ["De hand van %s: " % self.nick1]))
        self.assertTrue(self.output.privateMatch(self.nick1, ["De hand van %s: " % self.nick2]))
        self.assertTrue(self.output.privateMatch(self.nick2, ["De hand van %s: " % self.nick1]))
        self.assertFalse(self.output.privateMatch(self.nick2, ["De hand van %s: " % self.nick2]))
        self.assertTrue(self.output.match(["De beurt is aan %s." % self.nick1]))

    def test_WHEN_a_player_ask_for_the_rules_THEN_they_are_told(self):
        self.director.parse(self.nick2, "Wat zijn de spelregels?")
        self.assertTrue(self.output.match(["De spelregels zijn"]))

    def test_WHEN_one_says_Laten_we_shunting_spelen_THEN_he_is_reminded_of_the_current_game(self):
        self.director.parse(self.nick1, "Laten we shunting spelen.")
        self.assertTrue(self.output.match(["Sorry %s, je speelt al een spel met %s, %s!" % (self.nick1, self.nick1, self.nick2)]))

class GIVEN_a_just_started_game_with_two_players(unittest.TestCase):
    def setUp(self):
        self.output = MemoryStreamer()
        self.director = ShuntingDirector(self.output)
        self.nick1 = "hans"
        self.director.parse(self.nick1, "Laten we shunting spelen.")
        self.nick2 = "david"
        self.director.parse(self.nick2, "Ik doe mee met %s!" % self.nick1)
        self.director.parse(self.nick1, "We beginnen.")

    def test_WHEN_player1_says_Ik_leg_1_af_THEN_the_card_is_discarded_and_the_new_cards_are_secretly_told_to_player2(self):
        self.director.parse(self.nick1, "Ik leg 3 af.")
        self.assertTrue(self.output.privateMatch(self.nick1, ["De hand van %s: " % self.nick2]))
        self.assertTrue(self.output.privateMatch(self.nick2, ["De hand van %s: " % self.nick1, "De hand van %s: " % self.nick1]))
        self.assertTrue(self.output.match(["De beurt is aan %s." % self.nick2]))

    def test_WHEN_player1_says_Orden_kaarten_54321_THEN_his_cards_are_reordered_and_the_cards_are_secretly_told_to_player2_and_its_still_player1s_turn(self):
        self.director.parse(self.nick1, "Orden kaarten 54321")
        self.assertTrue(self.output.privateMatch(self.nick2, ["De hand van %s: " % self.nick1, "De hand van %s: " % self.nick1]))
        self.assertTrue(self.output.match(["De beurt is aan %s." % self.nick1]))

    def test_WHEN_player1_says_Speel_kaart_5_THEN_the_train_or_the_extraLocomotives_are_updated_and_his_new_hand_is_shown_to_others_and_it_is_told_who_is_next(self):
        self.director.parse(self.nick1, "Speel kaart 5")
        trainUpdate = self.output.match(["Trein [ROGBP] heeft "])
        extraLocomotivesUpdate = self.output.match(["Er zijn nog 2 noodlocomotieven"])
        self.assertTrue(trainUpdate != extraLocomotivesUpdate)
        self.assertTrue(self.output.privateMatch(self.nick2, ["De hand van %s: " % self.nick1, "De hand van %s: " % self.nick1]))
        self.assertTrue(self.output.match(["De beurt is aan %s." % self.nick2]))

    def test_WHEN_player1_says_Hint_David_3_THEN_that_player_is_hinted_and_hints_left_become_7_and_it_is_told_who_is_next(self):
        self.director.parse(self.nick1, "Hint David: Blaauw")
        hintCount = 0
        if self.output.match(["%s heeft geen B's" % self.nick2]):
            hintCount += 1
        if self.output.match(["Kaart [1-5] van %s is een B." % self.nick2]):
            hintCount += 1
        if self.output.match(["De kaarten [1-5](, [1-5])* en [1-5] van %s zijn B-en." % self.nick2]):
            hintCount += 1
        self.assertEqual(hintCount, 1)
        self.assertTrue(self.output.match(["Er mogen nog 7 hints"]))
        self.assertTrue(self.output.match(["De beurt is aan %s." % self.nick2]))

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
        self.director.parse(self.nick1, "Leg 1 af")
        self.assertTrue(self.output.match(["Jammer", "Er mag", "De beurt is aan %s." % self.nick2]))

    def test_WHEN_player1_says_Hint_David_B_THEN_that_player_is_hinted_and_hints_left_become_7_and_it_is_told_who_is_next(self):
        self.director.parse(self.nick1, "Hint speler David het prachtige getal van de eenheid: 3")
        hintCount = 0
        if self.output.match(["%s heeft geen 3's." % self.nick2]):
            hintCount += 1
        if self.output.match(["Kaart [1-5] van %s is een 3." % self.nick2]):
            hintCount += 1
        if self.output.match(["De kaarten [1-5](, [1-5])* en [1-5] van %s zijn 3-en." % self.nick2]):
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
        self.director.parse(self.nick2, "Hoeveel noodlocs hebben we nog?")
        self.assertTrue(self.output.match(["Er zijn nog 3 noodlocomotieven om foute wagons af te rangeren."]))

    def test_WHEN_a_player_ask_for_the_trains_THEN_that_is_told(self):
        self.director.parse(self.nick2, "Hoe staan onze treinen er voor?")
        self.assertTrue(self.output.match(["Trein B heeft nog geen enkele wagon."]))

    def test_WHEN_players_play_lots_of_wrong_cards_THEN_the_game_is_over_and_the_score_is_told(self):
        for i in range(5):
            self.director.parse(self.nick1, "Speel 1")
            self.director.parse(self.nick2, "Speel 1")
        self.assertTrue(self.output.match(["Het spel is afgelopen."]))
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