from collections import Counter
import unittest
from random import randint

"""
Percent farkles for 1 dice should be .66666
Score for 1 dice should be 1/6 * 100 + 1/6 * 50 = 25

Percent farkles for 2 die should be 2/3 * 2/3 = 4/9 = .44444
Score for 2 dice should be 1/36 * 200 + 1/18 * 150 + 1/36 * 100 + 2 * 1/6 * 2/3 * 100
 + 2 * 1/6 * 2/3 * 50 = 50
"""
def value_one_roll(num_dice, num_iterations):
    farkles = 0
    total_score = 0
    for i in range(num_iterations):
        dice = roll(num_dice)
        f = Farkle()
        moves = f.moves_and_scores(dice)
        best_score = moves.most_common(1)[0][1]
        total_score += best_score
        if best_score == 0:
            farkles += 1
    return (float(total_score) / num_iterations, float(farkles) / num_iterations) 


def ratio_to_3(moves, num_dice, current_score):
    """ hold dice with higest score per die ratio until rolling 3 or less dice"""
    best_move = ()
    best_ratio = 0
    for dice in moves:
        score = moves[dice]
        if len(dice) > 0 and score * 1.0 / len(dice) > best_ratio:
            best_move = dice
            best_ratio = score * 1.0 / len(dice)
    return (best_move, num_dice - len(best_move) > 3)

def ratio_to_4(moves, num_dice, current_score):
    """ hold dice with higest score per die ratio until rolling 2 or 1 dice"""
    best_move = ()
    best_ratio = 0
    for dice in moves:
        score = moves[dice]
        if len(dice) > 0 and score * 1.0 / len(dice) > best_ratio:
            best_move = dice
            best_ratio = score * 1.0 / len(dice)
    return (best_move, num_dice - len(best_move) > 2)

def best_to_4(moves, num_dice, current_score):
    """ Strategy; take max until rolling 2 or 1 dice """
    move, score = moves.most_common(1)[0]
    return (move, num_dice - len(move) > 2)

def best_to_3(moves, num_dice, current_score):
    """ Strategy; take max until rolling 2 or 1 dice """
    move, score = moves.most_common(1)[0]
    return (move, num_dice - len(move) > 3)

def best_to_2(moves, num_dice, current_score):
    """ Strategy; take max until rolling 2 or 1 dice """
    move, score = moves.most_common(1)[0]
    return (move, num_dice - len(move) > 4)

def best_to_3_or_4(moves, num_dice, current_score):
    move, score = moves.most_common(1)[0]
    roll_again = False
    if num_dice - len(move) > 3:
        roll_again = True
    if num_dice - len(move) == 3 and current_score + moves[move] < 300:
        roll_again = True
    return (move, roll_again)

def roll(num_dice):
    return [randint(1, 6) for x in range(num_dice)]

class Farkle:
    def __init__(self):
        self.dice = roll(6)
        self.subscore = 0

    def play_game(self, strategy, print_out = False):
        if print_out:
            print 'First roll: ' + str(self.dice)
        moves = self.moves_and_scores(self.dice)
        # check for farkle on first roll
        if len(moves) == 1:
            if print_out:
                print 'Farkle :('
            return 0
        move, roll_again = strategy(moves, len(self.dice), self.subscore)
        self.subscore += moves[move]
        if print_out:
            print 'Move: ' + str(move) + ' Score: ' + str(moves[move])
        while roll_again:
            if print_out:
                print 'You roll again'
            if move not in moves:
                if print_out:
                    print 'Illegal move'
                return False
            # roll again
            if len(self.dice) == len(move):
                self.dice = roll(6)
            else:
                self.dice = roll(len(self.dice) - len(move))
            moves = self.moves_and_scores(self.dice)
            # check for farkle
            if len(moves) == 1:
                if print_out:
                    print 'Roll: ' + str(self.dice)
                    print 'Farkle :('
                return 0
            move, roll_again = strategy(moves, len(self.dice), self.subscore)
            self.subscore += moves[move]
            if print_out:
                print 'Roll: ' + str(self.dice)
                print 'Move: ' + str(move) + ' Score: ' + str(moves[move])
        if print_out:
            print 'Final score:'
        return self.subscore

    def farkle(self, dice):
        """ Returns True if its a farkle, False otherwise. """
        moves = self.moves_and_scores(dice)
        return len(moves) == 1
    
    def max_move_and_score(self, dice):
        """
        Returns a tuple of the highest scoring move and that score
        """
        moves = self.moves_and_scores(dice)
        return moves.most_common(1)[0]

    def moves_and_scores(self, dice):
        moves = Counter()
        big_moves = self.big_moves(dice)
        ones_and_fives = self.moves_ones_and_fives(dice)
        moves = ones_and_fives | big_moves
        moves[()] = 0
        for move in big_moves:
            score = big_moves[move]
            extra_dice = set(dice) - set(move)
            extra_ones_and_fives = self.moves_ones_and_fives(list(extra_dice))
            for extra_move in extra_ones_and_fives:
                extra_score = extra_ones_and_fives[extra_move]
                new_move = tuple(sorted(move + extra_move))
                new_score = score + extra_score
                moves[new_move] = max(moves[new_move], new_score)
        return moves

    def big_moves(self, dice):
        """
        Helper for moves_and_scores.
        Returns all big moves that can be made with the 6 or less
        dice, as well as their score. In the form of a Counter with
        key tuple of dice rolled, and value numeric score.
        dice: An array of all dice rolled.
        """
        moves = Counter()
        if Farkle.six_of_a_kind(dice):
            moves[tuple(dice)] = max(3000, moves[tuple(dice)])
        elif Farkle.two_triplets(dice):
            held_dice = Farkle.two_triplets(dice)
            moves[tuple(dice[:3])] = max(dice[0] * 100, moves[tuple(dice[:3])])
            moves[tuple(dice[3:])] = max(dice[3] * 100, moves[tuple(dice[3:])])
            moves[tuple(dice)] = max(2500, moves[tuple(dice)])
        elif Farkle.straight(dice) or Farkle.three_pairs(dice):
            moves[tuple(dice)] = max(1500, moves[tuple(dice)])

        if Farkle.five_of_a_kind(dice):
            held_dice = Farkle.five_of_a_kind(dice)
            moves[tuple(held_dice)] = max(2000, moves[tuple(held_dice)]) 
        if Farkle.four_of_a_kind(dice):
            held_dice = Farkle.four_of_a_kind(dice)
            moves[tuple(held_dice)] = max(1000, moves[tuple(held_dice)])
        if Farkle.three_of_a_kind(dice):
            held_dice = Farkle.three_of_a_kind(dice)
            moves[tuple(held_dice)] = max(held_dice[0] * 100, moves[tuple(held_dice)])
        return moves

    def moves_ones_and_fives(self, dice):
        """
        Helper for moves_and_scores.
        Returns all combinations of 1's and 5's that can be withheld, as well as the
        score. Works for any number of dice. Returns too low a value for things like
        3+ one's and 3+ five's, but big moves overrides.
        """
        moves = Counter()
        ones = [1 for x in dice if x == 1]
        fives = [5 for x in dice if x == 5]
        for i in range(len(ones) + 1):
            for j in range(len(fives) + 1):
                moves[(1, )*i + (5, )*j] = max(100*i + 50*j, moves[(1, )*i + (5, )*j])
        return moves
    
    @staticmethod
    def straight(hand):
        if len(hand) != 6:
            return False
        for i in range(1,7):
            if i not in hand:
                return False
        return sorted(hand)

    @staticmethod
    def six_of_a_kind(hand):
        if len(hand) != 6:
            return False
        for die in hand:
            if hand[0] != die:
                return False
        return hand

    @staticmethod
    def two_triplets(hand):
        if len(hand) != 6:
            return False
        hand.sort()
        a, b, c, d, e, f = hand
        if a == b and b == c and d == e and e == f:
            return hand
        else:
            return False

    @staticmethod
    def three_pairs(hand):
        if len(hand) != 6:
            return False
        hand.sort()
        a, b, c, d, e, f = hand
        if a == b and c == d and e == f:
            return hand
        else:
            return False

    @staticmethod
    def five_of_a_kind(hand):
        if len(hand) != 6:
            return False
        c = Counter()
        for die in hand:
            c[die] += 1
        v = sorted(c.values())
        if v[-1] < 5:
            return False
        return [hand[0] if hand[0] == hand[1] else hand[2]]*5

    @staticmethod
    def four_of_a_kind(hand):
        c = Counter()
        for die in hand:
            c[die] += 1
        for i in range(1,7):
            if c[i] >= 4:
                return [i]*4
        return False

    @staticmethod
    def three_of_a_kind(hand):
        c = Counter()
        for die in hand:
            c[die] += 1
        v = sorted(c.values())
        to_return = []
        for i in range(1,7):
            if c[i] >= 3:
                return [i]*3
        return False

class TestFarkle(unittest.TestCase):
    def test_moves_and_scores(self):
        f = Farkle()
        self.assertEqual(f.moves_and_scores([6, 3, 2, 5, 3, 3]),
                         Counter({(3, 3, 3):300,
                                  (5, ):50,
                                  ():0,
                                  (3, 3, 3, 5):350}))
        self.assertEqual(f.moves_and_scores([1, 2, 1, 1, 5, 1]),
                                            Counter({():0,
                                                     (1, ):100,
                                                     (1, 1):200,
                                                     (1, 1, 1):300,
                                                     (1, 1, 1, 1):1000,
                                                     (5, ):50,
                                                     (1, 5):150,
                                                     (1, 1, 5):250,
                                                     (1, 1, 1, 5):350,
                                                     (1, 1, 1, 1, 5):1050}))
        self.assertEqual(f.moves_and_scores([6, 5, 6, 6, 5, 6]),
                                            Counter({():0,
                                                     (5, ):50,
                                                     (5, 5):100,
                                                     (6, 6, 6):600,
                                                     (5, 6, 6, 6):650,
                                                     (6, 6, 6, 6):1000,
                                                     (5, 6, 6, 6, 6):1050,
                                                     (5, 5, 6, 6, 6, 6):1500}))

    def test_big_moves(self):
        f = Farkle()
        self.assertEqual(f.big_moves([6, 3, 2, 5, 3, 3]),
                         Counter({(3, 3, 3):300}))
        self.assertEqual(f.big_moves([1, 2, 3, 3, 4, 5]),
                         Counter())
        self.assertEqual(f.big_moves([2, 1, 2, 2, 2, 2]),
                         Counter({(2, 2, 2):200,
                                  (2, 2, 2, 2):1000,
                                  (2, 2, 2, 2, 2):2000}))
        self.assertEqual(f.big_moves([6, 5, 6, 6, 5, 5]),
                         Counter({(5, 5, 5):500,
                                  (6, 6, 6):600,
                                  (5, 5, 5, 6, 6, 6):2500}))
                                  
                         

    def test_moves_ones_and_fives(self):
        f = Farkle()
        self.assertEqual(f.moves_ones_and_fives([1, 2, 3, 1, 5]),
                         Counter({():0, (1, ):100, (1, 1):200, (5, ):50,
                                  (1, 5):150, (1, 1, 5): 250}))
        self.assertEqual(f.moves_ones_and_fives([1, 2]),
                         Counter({():0, (1, ):100}))
        self.assertEqual(f.moves_ones_and_fives([2, 3, 3]),
                         Counter({():0}))

    def test_straight(self):
        self.assertEqual(Farkle.straight([1, 2, 3, 4, 5, 6]),
                         [1, 2, 3, 4, 5, 6])
        self.assertEqual(Farkle.straight([3, 2, 4, 1, 6, 5]),
                         [1, 2, 3, 4, 5, 6])
        self.assertFalse(Farkle.straight([1, 2, 3, 3, 4, 5]))
        self.assertFalse(Farkle.straight([1, 2, 3]))
        self.assertFalse(Farkle.straight([]))

    def test_six_of_a_kind(self):
        self.assertEqual(Farkle.six_of_a_kind([6, 6, 6, 6, 6, 6]),
                         [6, 6, 6, 6, 6, 6])
        self.assertEqual(Farkle.six_of_a_kind([3, 3, 3, 3, 3, 3]),
                         [3, 3, 3, 3, 3, 3])
        self.assertFalse(Farkle.straight([1, 2, 2, 2, 2, 2]))
        self.assertFalse(Farkle.straight([2, 2, 2, 2, 2]))

    def test_three_pairs(self):
        self.assertEqual(Farkle.three_pairs([2, 3, 1, 1, 2, 3]),
                         [1, 1, 2, 2, 3, 3])
        self.assertEqual(Farkle.three_pairs([4, 4, 3, 4, 3, 4]),
                         [3, 3, 4, 4, 4, 4])
        self.assertFalse(Farkle.three_pairs([1, 2, 2, 3, 3, 2]))
        self.assertFalse(Farkle.three_pairs([2, 2, 1, 1]))

    def test_two_triplets(self):
        self.assertEqual(Farkle.two_triplets([2, 3, 3, 2, 2, 3]),
                         [2, 2, 2, 3, 3, 3])
        self.assertEqual(Farkle.two_triplets([1, 1, 1, 6, 6, 6]),
                         [1, 1, 1, 6, 6, 6])
        self.assertFalse(Farkle.two_triplets([1, 2, 2, 3, 3, 3]))
        self.assertFalse(Farkle.two_triplets([2, 2, 1, 1]))

    def test_five_of_a_kind(self):
        self.assertEqual(Farkle.five_of_a_kind([3, 3, 3, 3, 2, 3]),
                         [3, 3, 3, 3, 3])
        self.assertEqual(Farkle.five_of_a_kind([1, 1, 1, 1, 1, 1]),
                         [1, 1, 1, 1, 1])
        self.assertFalse(Farkle.five_of_a_kind([1, 2, 3, 3, 3, 3]))
        self.assertFalse(Farkle.five_of_a_kind([2, 2, 2, 2]))

    def test_four_of_a_kind(self):
        self.assertEqual(Farkle.four_of_a_kind([2, 3, 4, 2, 2, 2]),
                         [2, 2, 2, 2])
        self.assertEqual(Farkle.four_of_a_kind([6, 6, 1, 6, 6, 6]),
                         [6, 6, 6, 6])
        self.assertFalse(Farkle.four_of_a_kind([1, 2, 2, 3, 3, 3]))
        self.assertFalse(Farkle.four_of_a_kind([2, 2, 2]))

    def test_three_of_a_kind(self):
        self.assertEqual(Farkle.three_of_a_kind([2, 3, 3, 4, 3, 2]),
                         [3, 3, 3])
        self.assertEqual(Farkle.three_of_a_kind([6, 6, 1, 6, 6, 6]),
                         [6, 6, 6])
        self.assertTrue(Farkle.three_of_a_kind([2, 2, 2, 4, 4, 4]))
        self.assertFalse(Farkle.three_of_a_kind([1, 2, 2, 1, 3, 3]))
        self.assertFalse(Farkle.three_of_a_kind([1, 2, 2, 1, 3, 3]))
        self.assertFalse(Farkle.three_of_a_kind([2, 2]))

if __name__ == '__main__':
#    unittest.main()

#    for i in range(1, 7):
#        print value_one_roll(i, 25000)
#    f = Farkle()
#    print f.play_game(best_to_3, True)

    ratio_3 = 0
    ratio_4 = 0
    best_4 = 0
    best_3 = 0
    best_3_or_4 = 0
    for i in range(5000):
        f = Farkle()
        ratio_3 += f.play_game(ratio_to_3)
        f = Farkle()
        ratio_4 += f.play_game(ratio_to_4)
        f = Farkle()
        best_4 += f.play_game(best_to_4)
        f = Farkle()
        best_3 += f.play_game(best_to_3)
        f = Farkle()
        best_3_or_4 += f.play_game(best_to_3_or_4)
    print 'Best ratio to 3'
    print ratio_3 / 5000.0
    print 'Best ratio to 4'
    print ratio_4 / 5000.0
    print 'Best to 3 or 4'
    print best_3_or_4 / 5000.0
    print 'Best to 3'
    print best_3 / 5000.0
    print 'Best to 4'
    print best_4 / 5000.0
