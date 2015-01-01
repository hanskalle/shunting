#!/usr/bin/python

import unittest
from HanabiGame import HanabiGame

class New_game(unittest.TestCase):
    def setUp(self):
        self.owner = "Hans"
        self.game = HanabiGame(self.owner)

    def test_The_owner_is_a_player_also(self):
        self.assertTrue(self.owner in self.game.getPlayers())

    def test_Cannot_start_the_game_yet(self):
        self.assertFalse(self.game.canStart())
        self.assertRaises(Exception, self.game.start)

    def test_Can_add_another_player(self):
        self.game.addPlayer("David")

    def test_After_adding_another_player_The_game_can_start(self):
        self.game.addPlayer("David")
        self.assertTrue(self.game.canStart())
        self.game.start()

    def test_Cannot_add_the_owner_again(self):
        self.assertRaises(Exception, self.game.addPlayer, self.owner)

    def test_Cannot_cannot_add_a_player_twice(self):
        self.game.addPlayer("David")
        self.assertRaises(Exception, self.game.addPlayer, "David")

class Five_player_game_in_setup(unittest.TestCase):
    def setUp(self):
        self.player1 = "Hans"
        self.player2 = "David"
        self.player3 = "Mattanja"
        self.player4 = "Arjan"
        self.player5 = "Joshua"
        self.game = HanabiGame(self.player1)
        self.game.addPlayer(self.player2)
        self.game.addPlayer(self.player3)
        self.game.addPlayer(self.player4)
        self.game.addPlayer(self.player5)

    def test_You_cannot_add_an_extra_player(self):
        self.assertRaises(Exception, self.game.addPlayer, "Joop")

    def test_After_removing_one_of_the_players_There_are_4_players_left(self):
        self.game.removePlayer(self.player3)
        self.assertEquals(self.game.getNumberOfPlayers(), 4)

    def test_After_removing_a_player_Can_add_him_again(self):
        self.game.removePlayer(self.player3)
        self.game.addPlayer(self.player3)

    def test_After_starting_the_game_Cannot_remove_one_of_the_players(self):
        self.game.start()
        self.assertRaises(Exception, self.game.removePlayer, self.player3)

    def test_Cannot_remove_an_unknown_player(self):
        self.assertRaises(Exception, self.game.removePlayer, "unknown-player")

    def test_Cannot_remove_the_owner_of_the_game(self):
        self.assertRaises(Exception, self.game.removePlayer, self.player1)

class Just_started_2_player_game(unittest.TestCase):
    def setUp(self):
        self.player1 = "Hans"
        self.player2 = "David"
        self.game = HanabiGame(self.player1)
        self.game.addPlayer(self.player2)
        self.game.start()

    def test_Cannot_setup_anything_anymore(self):
        self.assertRaises(Exception,  self.game._setupTrainsForTest,  ["R1"])
        self.assertRaises(Exception,  self.game._setupHandForTest,  ["R1"])
        self.assertRaises(Exception,  self.game._setupDeckForTest,  ["R1"])

    def test_First_player_takes_the_first_turn(self):
        self.assertEqual(self.game.getActivePlayer() , self.player1)

    def test_Cannot_start_game_again(self):
        self.assertFalse(self.game.canStart())
        self.assertRaises(Exception, self.game.start)

    def test_Cannot_add_players(self):
        self.assertRaises(Exception, self.game.addPlayer, "Arjan")
        
    def test_Players_hold_5_cards(self):
        self.assertEqual(self.game.getNumberOfHandCards(self.player1), 5)
        self.assertEqual(self.game.getNumberOfHandCards(self.player2), 5)

    def test_There_are_3_Thunderstorms_left(self):
        self.assertEqual(self.game.getThunderstormsLeft(), 3);

    def test_There_are_8_hints_left(self):
        self.assertEqual(self.game.getHintsLeft(), 8);
        
    def test_Deck_has_40_cards_left(self):
        self.assertEqual(self.game.getNumberOfCardsInDeck(), 40);
        
    def test_Game_is_on(self):
        self.assertTrue(self.game.isOn())
        
    def test_Game_is_not_over(self):
        self.assertFalse(self.game.isOver())
        
    def test_Score_is_0(self):
        self.assertEqual(self.game.getScore(), 0)
        
    def test_First_player_can_hint_the_other(self):
        self.game.hint(self.player2, "1")
        
    def test_First_player_cannot_hint_himself(self):
        self.assertRaises(Exception, self.game.hint, self.player1, "1")
        
    def test_First_player_can_discard_his_first_card(self):
        self.game.discard(1)

    def test_First_player_cannot_discard_his_sixth_card(self):
        self.assertRaises(Exception,  self.game.discard,  6)

    def test_Players_can_discard_21_times_each(self):
        for i in range(21):
            for player in self.game.getPlayers():
                self.game.discard(1)

    def test_After_discarding_42_cards_Game_is_over(self):
        for i in range(42):
            self.game.discard(1)
        self.assertTrue(self.game.isOver())

    def test_Players_can_hint_8_times_in_a_row(self):
        for i in range(4):
            self.game.hint(self.player2, "R")
            self.game.hint(self.player1, "1")

    def test_Players_cannot_hint_9_times_in_a_row(self):
        for i in range(4):
            self.game.hint(self.player2, "R")
            self.game.hint(self.player1, "1")
        self.assertRaises(Exception, self.game.hint, self.player2, "R")

    def test_First_player_cannot_play_his_sixth_card(self):
        self.assertRaises(Exception,  self.game.play,  6)

    def test_After_first_player_discards_Second_player_takes_his_turn(self):
        self.game.discard(1)
        self.assertEqual(self.game.getActivePlayer(), self.player2)
        
    def test_After_both_players_discard_First_player_takes_his_turn_again(self):
        self.game.discard(1)
        self.game.discard(1)
        self.assertEqual(self.game.getActivePlayer(), self.player1)
        
    def test_After_discarding_10_cards_Deck_has_30_cards_left(self):
        for i in range(10):
            self.game.discard(1)
        self.assertEqual(self.game.getNumberOfCardsInDeck(), 30);

class Just_started_3_player_game(unittest.TestCase):
    def setUp(self):
        self.player1 = "Hans"
        self.player2 = "David"
        self.player3 = "Mattanja"
        self.game = HanabiGame(self.player1)
        self.game.addPlayer(self.player2)
        self.game.addPlayer(self.player3)
        self.game.start()

    def test_All_players_hold_5_cards(self):
        for player in self.game.getPlayers():
            self.assertEqual(self.game.getNumberOfHandCards(player), 5)

class Just_started_4_player_game(unittest.TestCase):
    def setUp(self):
        self.player1 = "Hans"
        self.player2 = "David"
        self.player3 = "Mattanja"
        self.player4 = "Arjan"
        self.game = HanabiGame(self.player1)
        self.game.addPlayer(self.player2)
        self.game.addPlayer(self.player3)
        self.game.addPlayer(self.player4)
        self.game.start()

    def test_All_players_hold_4_cards(self):
        for player in self.game.getPlayers():
            self.assertEqual(self.game.getNumberOfHandCards(player), 4)

class Just_started_5_player_game(unittest.TestCase):
    def setUp(self):
        self.player1 = "Hans"
        self.player2 = "David"
        self.player3 = "Mattanja"
        self.player4 = "Arjan"
        self.player5 = "Joshua"
        self.game = HanabiGame(self.player1)
        self.game.addPlayer(self.player2)
        self.game.addPlayer(self.player3)
        self.game.addPlayer(self.player4)
        self.game.addPlayer(self.player5)
        self.game.start()

    def test_All_players_hold_4_cards(self):
        for player in self.game.getPlayers():
            self.assertEqual(self.game.getNumberOfHandCards(player), 4)

class Two_just_started_2_player_games(unittest.TestCase):
    def setUp(self):
        self.player1 = "Hans"
        self.player2 = "David"
        self.game1 = HanabiGame(self.player1)
        self.game1.addPlayer(self.player2)
        self.game1.start()
        self.game2 = HanabiGame(self.player1)
        self.game2.addPlayer(self.player2)
        self.game2.start()

    def test_Hands_of_the_first_players_in_both_games_should_not_be_equal(self):
        self.assertNotEqual(self.game1.getHandCards(self.player1),  self.game2.getHandCards(self.player2))

class Game_with_all_wrong_cards_on_top_of_the_deck(unittest.TestCase):
    def setUp(self):
        self.player1 = "Hans"
        self.player2 = "David"
        self.game = HanabiGame(self.player1)
        self.game.addPlayer(self.player2)
        self.game._setupDeckForTest(["R5", "O5", "G5", "B5", "P5", "R4", "O4", "G4", "B4", "P4"]) 
        self.game.start()

    def test_After_playing_2_cards_Game_is_not_over(self):
        self.game.play(1)
        self.game.play(1)
        self.assertFalse(self.game.isOver())

    def test_After_playing_3_cards_Game_is_over(self):
        self.game.play(1)
        self.game.play(1)
        self.game.play(2)
        self.assertTrue(self.game.isOver())

class Game_with_a_perfect_setup_on_table_hand_and_deck(unittest.TestCase):
    def setUp(self):
        self.player1 = "Hans"
        self.player2 = "David"
        self.game = HanabiGame(self.player1)
        self.game.addPlayer(self.player2)
        self.game._setupTrainsForTest(["O1","G1","G2","B1","B2","B3"])
        self.game._setupHandForTest(self.player1, ["R1","O2","G3","B4","B5"])
        self.game._setupHandForTest(self.player2, ["R2","O3","G4","R3","R4"])
        self.game._setupDeckForTest(["R5", "O4", "O5", "G4", "G5", "P1",  "P2", "P3",  "P4",  "P5"]) 
        self.game.start()

    def test_Player1_can_reorder_his_hand_cards(self):
        self.game.reorderHandCards(self.player1, [3,5,2,1,4])
        self.assertEqual(self.game.getHandCards(self.player1), ["G3","B5","O2","R1","B4"])

    def test_Player2_can_reorder_his_hand_cards(self):
        self.game.reorderHandCards(self.player2, [5,4,3,2,1])
        self.assertEqual(self.game.getHandCards(self.player2), ["R4","R3","G4","O3","R2"])

    def test_After_reordering_his_hand_cards_Player_still_his_turn(self):
        self.game.reorderHandCards(self.player1, [3,5,2,1,4])
        self.assertEqual(self.game.getActivePlayer(), self.player1)

    def test_Both_players_hold_5_cards(self):
        self.assertEqual(self.game.getNumberOfHandCards(self.player1), 5)
        self.assertEqual(self.game.getNumberOfHandCards(self.player2), 5)

    def test_Player1_hold_cards_R1_O2_G3_B4_B5(self):
        self.assertEqual(self.game.getHandCards(self.player1), ["R1","O2","G3","B4","B5"])

    def test_Hinting_player2_with_3_should_result_in_FTFTF(self):
        self.assertEqual(self.game.hint(self.player2, "3"), [False, True, False, True, False])

    def test_Hinting_player2_with_O_should_result_in_FTFFF(self):
        self.assertEqual(self.game.hint(self.player2, "O"), [False, True, False, False, False])

    def test_Train_length_of_B_is_3(self):
        self.assertEqual(self.game.getTrainLength("B"), 3)

    def test_After_player1_playing_his_first_card_five_times_and_player2_just_discarding_Score_is_11(self):
        for i in range(5):
            self.game.play(i+1)
            self.game.discard(1)
        self.assertEqual(self.game.getScore(), 11)

    def test_After_Hinting_2_times_and_completing_a_train_Hints_should_be_7(self):
        for i in range(2):
            self.game.play(4+i)
            self.game.hint(self.player1,  "B")
        self.assertEqual(self.game.getHintsLeft(), 7)
        
    def test_After_playing_a_wrong_card_Thunderstorms_decreases_by_1(self):
        self.game.play(5)
        self.assertEqual(self.game.getThunderstormsLeft(), 2)
        
    def test_After_discards_a_card_with_8_hints_Hints_is_not_increased(self):
        self.game.discard(1)
        self.assertEqual(self.game.getHintsLeft(), 8)
        
    def test_After_hinting_2_times_Hints_is_decreased_by_2(self):
        self.game.hint(self.player2, "1")
        self.game.hint(self.player1, "1")
        self.game.play(1)
        self.game.play(1)
        self.assertEqual(self.game.getHintsLeft(), 6)
        
    def test_After_hinting_2_times_and_discarding_2_times_Hints_should_be_8_again(self):
        self.game.hint(self.player2, "1")
        self.game.hint(self.player1, "1")
        self.game.discard(1)
        self.game.discard(1)
        self.assertEqual(self.game.getHintsLeft(), 8)
        
    def test_After_playing_20_cards_Score_is_perfect(self):
        for i in range(10):
            self.game.play((i % 5) + 1)
            self.game.play((i % 5) + 1)
        self.assertEqual(self.game.getScore(), 25)

        
    def test_After_playing_20_cards_Game_is_over(self):
        for i in range(10):
            self.game.play((i % 5) + 1)
            self.game.play((i % 5) + 1)
        self.assertTrue(self.game.isOver())
        
    def test_First_5_cards_drawn_are_R5_O4_O5_G4_G5(self):
        self.game.discard(1)
        self.assertEqual(self.game._peekHandCard(1, self.player1), "R5")
        self.game.discard(1)
        self.assertEqual(self.game._peekHandCard(1, self.player2), "O4")
        self.game.discard(1)
        self.assertEqual(self.game._peekHandCard(1, self.player1), "O5")
        self.game.discard(1)
        self.assertEqual(self.game._peekHandCard(1, self.player2), "G4")
        self.game.discard(1)
        self.assertEqual(self.game._peekHandCard(1, self.player1), "G5")
        
if __name__ == '__main__':
    unittest.main()       
