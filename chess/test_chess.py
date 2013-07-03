from chess import *
import unittest

class TestBoard(unittest.TestCase):
  def test_equals(self):
    a = Board()
    b = Board()
    self.assertEqual(a, b)

    a = Board()
    b = Board()
    a.turn = Color.white
    b.turn = Color.black
    self.assertFalse(a == b)

class TestPawn(unittest.TestCase):
  def test_basic_move(self):
    b = Board()
    p = Pawn(Location(2, 2))
    b.pieces = [p]
    test_moves = p.legal_moves(b)

    new_b = Board()
    new_b.pieces = [Pawn(Location(3, 2))]
    actual_moves = [new_b]

    self.assertEqual(set(test_moves), set(actual_moves))

  def test_blocked_move(self):
    b = Board()
    black_pawn = Pawn(Location(2, 2), Color.black)
    white_pawn = Pawn(Location(3, 2), Color.white)
    b.pieces = [black_pawn, white_pawn]
    test_moves = black_pawn.legal_moves(b)

    actual_moves = []

    print test_moves[0]

    self.assertEqual(set(test_moves), set(actual_moves))

  def test_first_move(self):
    b = Board()
    p = Pawn(Location(1, 2))
    b.pieces = [p]
    test_moves = p.legal_moves(b)

    new_b1 = Board()
    new_b1.pieces = [Pawn(Location(3, 2))]
    new_b2 = Board()
    new_b2.pieces = [Pawn(Location(2, 2))]
    actual_moves = [new_b1, new_b2]

    self.assertEqual(set(test_moves), set(actual_moves))

#  def test_edge(self):

#  def test_capture(self):

#  def test_upgrade(self):

#  def test_upgrade_capture(self):


if __name__ == "__main__":
  unittest.main()
