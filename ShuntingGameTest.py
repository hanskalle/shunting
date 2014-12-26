#!/usr/bin/python

import unittest
from ShuntingGame import ShuntingGame

class GIVEN_a_new_shunting_game(unittest.TestCase):
    def setUp(self):
        self.owner = "Hans"
        self.game = ShuntingGame(self.owner)

    def test_THEN_the_owner_is_a_player_also(self):
        self.assertTrue(self.owner in self.game.getPlayers())

    def test_THEN_the_game_cannot_start_yet(self):
        self.assertFalse(self.game.canStart())
        self.assertRaises(Exception, self.game.start)

    def test_WHEN_you_add_another_player_THEN_the_game_can_start(self):
        self.game.addPlayer("David")
        self.assertTrue(self.game.canStart())
        self.game.start()

    def test_WHEN_the_owner_adds_himself_again_THEN_that_is_not_allowed(self):
        self.assertRaises(Exception, self.game.addPlayer, self.owner)

    def test_WHEN_a_player_is_added_twice_THEN_that_is_not_allowed(self):
        self.game.addPlayer("David")
        self.assertRaises(Exception, self.game.addPlayer, "David")

class GIVEN_a_just_started_shunting_game_with_two_players(unittest.TestCase):
    def setUp(self):
        self.player1 = "Hans"
        self.player2 = "David"
        self.game = ShuntingGame(self.player1)
        self.game.addPlayer(self.player2)
        self.game.start()

    def test_THEN_you_cannot_setup_anything_anymore(self):
        self.assertRaises(Exception,  self.game._setupTrainsForTest,  ["R1"])
        self.assertRaises(Exception,  self.game._setupHandForTest,  ["R1"])
        self.assertRaises(Exception,  self.game._setupDeckForTest,  ["R1"])

    def test_THEN_the_first_player_takes_the_first_turn(self):
        self.assertEqual(self.game.getActivePlayer() , self.player1)

    def test_THEN_the_game_cannot_start_again(self):
        self.assertFalse(self.game.canStart())
        self.assertRaises(Exception, self.game.start)

    def test_THEN_new_players_cannot_be_added(self):
        self.assertRaises(Exception, self.game.addPlayer, "Arjan")
        
    def test_THEN_both_players_hold_5_cards(self):
        self.assertEqual(self.game.getNumberOfHandCards(self.player1), 5)
        self.assertEqual(self.game.getNumberOfHandCards(self.player2), 5)

    def test_THEN_there_are_3_ExtraLocomotives_left(self):
        self.assertEqual(self.game.getExtraLocomotivesLeft(), 3);

    def test_THEN_there_are_8_hints_left(self):
        self.assertEqual(self.game.getHintsLeft(), 8);
        
    def test_THEN_the_deck_has_40_cards_left(self):
        self.assertEqual(self.game._getNumberOfCardsInDeck(), 40);
        
    def test_THEN_the_game_is_not_over(self):
        self.assertFalse(self.game.isOver())
        
    def test_THEN_the_score_is_0(self):
        self.assertEqual(self.game.getScore(), 0)
        
    def test_THEN_first_player_can_hint_the_other(self):
        self.game.hint(self.player2, "1")
        
    def test_THEN_first_player_cannot_hint_itself(self):
        self.assertRaises(Exception, self.game.hint, self.player1, "1")
        
    def test_THEN_first_player_can_discard_his_first_card(self):
        self.game.discard(1)

    def test_THEN_first_player_cannot_discard_his_sixth_card(self):
        self.assertRaises(Exception,  self.game.discard,  6)

    def test_THEN_the_players_can_discard_21_times_each(self):
        for i in range(21):
            for player in self.game.getPlayers():
                self.game.discard(1)

    def test_WHEN_the_players_discard_42_times_THEN_the_game_is_over(self):
        for i in range(42):
            self.game.discard(1)
        self.assertTrue(self.game.isOver())

    def test_THEN_the_players_can_hint_8_times_in_a_row(self):
        for i in range(4):
            self.game.hint(self.player2, "R")
            self.game.hint(self.player1, "1")

    def test_THEN_the_players_cannot_hint_9_times_in_a_row(self):
        for i in range(4):
            self.game.hint(self.player2, "R")
            self.game.hint(self.player1, "1")
        self.assertRaises(Exception, self.game.hint, self.player2, "R")

    def test_THEN_first_player_cannot_play_his_sixth_card(self):
        self.assertRaises(Exception,  self.game.play,  6)

    def test_WHEN_the_first_player_discards_THEN_the_second_player_takes_his_turn(self):
        self.game.discard(1)
        self.assertEqual(self.game.getActivePlayer(), self.player2)
        
    def test_WHEN_both_players_discard_THEN_the_first_player_takes_his_turn_again(self):
        self.game.discard(1)
        self.game.discard(1)
        self.assertEqual(self.game.getActivePlayer(), self.player1)
        
    def test_WHEN_there_are_10_cards_discarded_THEN_there_are_30_cards_left_in_the_deck(self):
        for i in range(10):
            self.game.discard(1)
        self.assertEqual(self.game._getNumberOfCardsInDeck(), 30);

class GIVEN_a_just_started_shunting_game_with_three_players(unittest.TestCase):
    def setUp(self):
        self.player1 = "Hans"
        self.player2 = "David"
        self.player3 = "Mattanja"
        self.game = ShuntingGame(self.player1)
        self.game.addPlayer(self.player2)
        self.game.addPlayer(self.player3)
        self.game.start()

    def test_THEN_all_players_hold_5_cards(self):
        for player in self.game.getPlayers():
            self.assertEqual(self.game.getNumberOfHandCards(player), 5)

class GIVEN_a_just_started_shunting_game_with_four_players(unittest.TestCase):
    def setUp(self):
        self.player1 = "Hans"
        self.player2 = "David"
        self.player3 = "Mattanja"
        self.player4 = "Arjan"
        self.game = ShuntingGame(self.player1)
        self.game.addPlayer(self.player2)
        self.game.addPlayer(self.player3)
        self.game.addPlayer(self.player4)
        self.game.start()

    def test_THEN_all_players_hold_4_cards(self):
        for player in self.game.getPlayers():
            self.assertEqual(self.game.getNumberOfHandCards(player), 4)

class GIVEN_a_just_started_shunting_game_with_five_players(unittest.TestCase):
    def setUp(self):
        self.player1 = "Hans"
        self.player2 = "David"
        self.player3 = "Mattanja"
        self.player4 = "Arjan"
        self.player5 = "Joshua"
        self.game = ShuntingGame(self.player1)
        self.game.addPlayer(self.player2)
        self.game.addPlayer(self.player3)
        self.game.addPlayer(self.player4)
        self.game.addPlayer(self.player5)
        self.game.start()

    def test_THEN_all_players_hold_4_cards(self):
        for player in self.game.getPlayers():
            self.assertEqual(self.game.getNumberOfHandCards(player), 4)

class GIVEN_two_just_started_shunting_games_with_two_players(unittest.TestCase):
    def setUp(self):
        self.player1 = "Hans"
        self.player2 = "David"
        self.game1 = ShuntingGame(self.player1)
        self.game1.addPlayer(self.player2)
        self.game1.start()
        self.game2 = ShuntingGame(self.player1)
        self.game2.addPlayer(self.player2)
        self.game2.start()

    def test_THEN_the_hands_of_the_active_player_in_both_games_should_not_be_equal(self):
        self.assertNotEqual(self.game1.getHandCards(self.player1),  self.game2.getHandCards(self.player2))

class GIVEN_a_shunting_game_with_all_wrong_cards_on_top_of_the_deck(unittest.TestCase):
    def setUp(self):
        self.player1 = "Hans"
        self.player2 = "David"
        self.game = ShuntingGame(self.player1)
        self.game.addPlayer(self.player2)
        self.game._setupDeckForTest(["R5", "O5", "G5", "B5", "P5", "R4", "O4", "G4", "B4", "P4"]) 
        self.game.start()

    def test_WHEN_there_were_2_cards_played_THEN_then_game_is_not_over(self):
        self.game.play(1)
        self.game.play(1)
        self.assertFalse(self.game.isOver())

    def test_WHEN_there_were_3_cards_played_THEN_then_game_is_over(self):
        self.game.play(1)
        self.game.play(1)
        self.game.play(1)
        self.assertTrue(self.game.isOver())

class GIVEN_a_shunting_game_with_a_perfect_setup_on_table_hand_and_deck(unittest.TestCase):
    def setUp(self):
        self.player1 = "Hans"
        self.player2 = "David"
        self.game = ShuntingGame(self.player1)
        self.game.addPlayer(self.player2)
        self.game._setupTrainsForTest(["O1","G1","G2","B1","B2","B3"])
        self.game._setupHandForTest(self.player1, ["R1","O2","G3","B4","B5"])
        self.game._setupHandForTest(self.player2, ["R2","O3","G4","R3","R4"])
        self.game._setupDeckForTest(["R5", "O4", "O5", "G4", "G5", "P1",  "P2", "P3",  "P4",  "P5"]) 
        self.game.start()

    def test_THEN_player1_can_reorder_his_hand_cards(self):
        self.game.reorderHandCards(self.player1, [3,5,2,1,4])
        self.assertEqual(self.game.getHandCards(self.player1), ["G3","B5","O2","R1","B4"])

    def test_THEN_player2_can_reorder_his_hand_cards(self):
        self.game.reorderHandCards(self.player2, [5,4,3,2,1])
        self.assertEqual(self.game.getHandCards(self.player2), ["R4","R3","G4","O3","R2"])

    def test_WHEN_player1_reorders_his_hand_cards_THEN_its_still_his_turn(self):
        self.game.reorderHandCards(self.player1, [3,5,2,1,4])
        self.assertEqual(self.game.getActivePlayer(), self.player1)

    def test_THEN_both_players_hold_5_cards(self):
        self.assertEqual(self.game.getNumberOfHandCards(self.player1), 5)
        self.assertEqual(self.game.getNumberOfHandCards(self.player2), 5)

    def test_THEN_player1_hold_the_cards_R1_O2_G3_B4_B5(self):
        self.assertEqual(self.game.getHandCards(self.player1), ["R1","O2","G3","B4","B5"])

    def test_THEN_hinting_player2_with_3_should_result_in_FTFTF(self):
        self.assertEqual(self.game.hint(self.player2, "3"), [False, True, False, True, False])

    def test_THEN_hinting_player2_with_O_should_result_in_FTFFF(self):
        self.assertEqual(self.game.hint(self.player2, "O"), [False, True, False, False, False])

    def test_THEN_train_length_of_B_is_3(self):
        self.assertEqual(self.game.getTrainLength("B"), 3)

    def test_WHEN_player1_plays_his_first_card_five_times_AND_player2_just_discards_THEN_the_score_should_be_11(self):
        for i in range(5):
            self.game.play(1)
            self.game.discard(1)
        self.assertEqual(self.game.getScore(), 11)

    # completing a train gets an extra hint
    def test_WHEN_player1_plays_his_fourth_card_two_times_AND_player2_hints_two_times_THEN_there_should_be_7_hints_left(self):
        for i in range(2):
            self.game.play(4)
            self.game.hint(self.player1,  "B")
        self.assertEqual(self.game.getHintsLeft(), 7)
        
    # playing a wrong card costs a defect
    def test_WHEN_playing_the_fifth_card_THEN_there_are_2_ExtraLocomotives_left(self):
        self.game.play(5)
        self.assertEqual(self.game.getExtraLocomotivesLeft(), 2)
        
    def test_WHEN_the_first_player_discards_its_first_card_THEN_the_number_of_hints_left_is_still_8(self):
        self.game.discard(1)
        self.assertEqual(self.game.getHintsLeft(), 8)
        
    def test_WHEN_two_hints_are_given_AND_two_correct_cards_are_played_THEN_the_number_of_hints_left_is_6(self):
        self.game.hint(self.player2, "1")
        self.game.hint(self.player1, "1")
        self.game.play(1)
        self.game.play(1)
        self.assertEqual(self.game.getHintsLeft(), 6)
        
    def test_WHEN_two_hints_are_given_AND_two_cards_are_discarded_THEN_the_number_of_hints_left_is_8_again(self):
        self.game.hint(self.player2, "1")
        self.game.hint(self.player1, "1")
        self.game.discard(1)
        self.game.discard(1)
        self.assertEqual(self.game.getHintsLeft(), 8)
        
    def test_WHEN_the_players_play_their_first_card_20_times_THEN_the_game_is_over_and_the_score_is_perfect(self):
        for i in range(20):
            self.game.play(1)
        self.assertEqual(self.game.getScore(), 25)
        self.assertTrue(self.game.isOver())
        
    def test_THEN_the_first_cards_drawn_should_be_R5_O4_O5_G4_G5(self):
        self.game.discard(1)
        self.assertEqual(self.game._peekHandCard(5, self.player1), "R5")
        self.game.discard(1)
        self.assertEqual(self.game._peekHandCard(5, self.player2), "O4")
        self.game.discard(1)
        self.assertEqual(self.game._peekHandCard(5, self.player1), "O5")
        self.game.discard(1)
        self.assertEqual(self.game._peekHandCard(5, self.player2), "G4")
        self.game.discard(1)
        self.assertEqual(self.game._peekHandCard(5, self.player1), "G5")
        
if __name__ == '__main__':
    unittest.main()       
