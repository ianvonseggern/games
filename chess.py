import unittest

class Location(object):
  row_range = range(8)
  col_range = range(8)

  def __init__(self, row = 0, col = 0):
    if row not in self.row_range or col not in self.col_range:
  	  raise Exception('Illegal location ' + str(row) + ', ' + str(col))
    self.row = row
    self.col = col

  @classmethod
  def in_range(self, row, col):
    return row in self.row_range and col in self.col_range

  def __eq__(self, other_location):
    return self.row == other_location.row and self.col == other_location.col

  def __str__(self):
    return str(self.row) + ', ' + str(self.col)

class Color(object):
  black = 'BLACK'
  white = 'WHITE'

class Piece(object):
  def __init__(self, location = Location(), color = Color.black,
               name = 'DEFAULT', letter = 'D'):
    self.location = location
    self.color = color
    self.name = name
    self.letter = letter

  def legal_moves(self, board):
    return []

  def copy(self):
    p = self.__class__()
    p.color = self.color
    p.name = self.name
    p.letter = self.letter
    p.location = Location(self.location.row, self.location.col)
    return p

  def __str__(self):
    return self.color + ' ' + self.name + ' at ' + str(self.location)

  def __eq__(self, p):
    return (self.color == p.color and self.name == p.name and
            self.letter == p.letter and self.location == p.location)
      
class Board(object):
  def __init__(self):
    self.turn = Color.white
    self.pieces = self.reset_pieces()

  def reset_pieces(self):
    pieces = []

    # Create pawns
    for i in range(8):
      pieces.append(Pawn(Location(1, i), Color.white))
      pieces.append(Pawn(Location(6, i), Color.black))

    # Rooks, Knights, Bishops
    pieces.append(Rook(Location(0, 0), Color.white))
    pieces.append(Rook(Location(0, 7), Color.white))
    pieces.append(Rook(Location(7, 0), Color.black))
    pieces.append(Rook(Location(7, 7), Color.black))

    pieces.append(Knight(Location(0, 1), Color.white))
    pieces.append(Knight(Location(0, 6), Color.white))
    pieces.append(Knight(Location(7, 1), Color.black))
    pieces.append(Knight(Location(7, 6), Color.black))

    pieces.append(Bishop(Location(0, 2), Color.white))
    pieces.append(Bishop(Location(0, 5), Color.white))
    pieces.append(Bishop(Location(7, 2), Color.black))
    pieces.append(Bishop(Location(7, 5), Color.black))

    # Queens and Kings
    pieces.append(Queen(Location(0, 3), Color.white))
    pieces.append(Queen(Location(7, 3), Color.black))
    pieces.append(King(Location(0, 4), Color.white))
    pieces.append(King(Location(7, 4), Color.black))

    return pieces

  def at_location(self, location):
    """ Returns what is at a specific location. """
    for piece in self.pieces:
      if piece.location == location:
        return piece
    return None

  def check_legal(self):
     """ Maybe include this to see if the current board is legal or not?"""
     raise Exception('Not Implemented')

  def move(self, start_location, end_location):
    """
    Does not check if the move is legal (thats up to the piece,
    as the rules are differnt for each). Creates a new copy of the board,
    and takes a start location and moves the piece at that location to the
    end location, capturing if necessary.
    """
    new_board = self.copy()
    # Capture if a piece exists at end location
    capture_piece = new_board.at_location(end_location)
    if capture_piece:
      new_board.pieces.remove(capture_piece)
    # Move piece
    new_board.at_location(start_location).location = end_location
    return new_board

  def copy(self):
    rtn = Board()
    rtn.pieces = []
    rtn.turn = self.turn
    for piece in self.pieces:
      rtn.pieces.append(piece.copy())
    return rtn

  def __str__(self):
    rtn = ""
    # Print board from top to bottom, high indicies first.
    for i in (7, 6, 5, 4, 3, 2, 1, 0):
      rtn += str(i+1) + ' '
      for j in range(8):
        piece = self.at_location(Location(i, j))
        if piece:
          rtn += piece.letter
        else:
          rtn += ' '
      rtn += '\n'
    rtn += '\n  abcdefgh'
    return rtn

  def __eq__(self, board):
    if len(self.pieces) != len(board.pieces):
      return False
    for piece in self.pieces:
      if piece not in board.pieces:
        return False
    if board.turn != self.turn:
      return False
    return True

  def __hash__(self):
    return str(self).__hash__()

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

class Pawn(Piece):
  def __init__(self, location = Location(), color = Color.black):
    super(Pawn, self).__init__(location, color, 'Pawn', 'P' if color == Color.white else 'p')

  def legal_moves(self, board):
    rtn = []
    col = self.location.col
    # First move can go two
    if (self.location.row == 1 and not board.at_location(Location(2,col)) and
        not board.at_location(Location(3,col))):
      rtn.append(board.move(self.location, Location(3, col)))
    # Move forward one
    row = self.location.row + 1
    col = self.location.col
    if (Location.in_range(row, col) and
        not board.at_location(Location(row, col))):
      if row < 7:
        rtn.append(board.move(self.location, Location(row, col)))
      else:
        rtn.extend(self.pawn_upgrade(board, self.location,
                                     Location(row, col)))
    # Captures
    for col_delta in [-1, 1]:
      row = self.location.row + 1
      col = self.location.col + col_delta 
      if Location.in_range(row, col):
        capture_piece = board.at_location(Location(row, col))
        if capture_piece and capture_piece.color != self.color:
          if row < 7:
            rtn.append(board.move(self.location,
                                  Location(row, col)))
          else:
            rtn.extend(self.pawn_upgrade(board, self.location,
                                         Location(row, col)))
    # Enpasant TODO
    return rtn

  def pawn_upgrade(board, old_location, new_location):
    rtn = []
    for piece in [Pawn, Bishop, Rook, Knight, Queen]:
      new_board = board.move(old_location, new_location)
      new_piece = new_board.at_location(new_location)
      new_board.pieces.remove(new_piece)
      new_baord.pieces.append(piece(Location(new_location)))
      rtn.append(new_board)
    return rtn

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

class Rook(Piece):
  def __init__(self, location = Location(), color = Color.black):
  	super(Rook, self).__init__(location, color, 'Rook', 'R' if color == Color.white else 'r')

  def legal_moves(self, board):
    rtn = []
    for r_delta, c_delta in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
      r = self.location.row + r_delta
      c = self.location.col + c_delta
      if Location.in_range(r, c):
        piece = board.at_location(Location(r, c))
        while not piece and Location.in_range(r, c):
          rtn.append(board.move(self.location, Location(r, c)))
          r += r_delta
          c += c_delta
          if Location.in_range(r, c):
            piece = board.at_location(Location(r, c))
          else:
            piece = None
        if piece and piece.color != self.color:
          rtn.append(board.move(self.location, Location(r, c)))
    return rtn

class Knight(Piece):
  def __init__(self, location = Location(), color = Color.black):
    super(Knight, self).__init__(location, color, 'Knight', 'N' if color == Color.white else 'n')

  def legal_moves(self, board):
    rtn = []
    for r_delta, c_delta in [(1, 2), (1, -2), (2, 1), (2, -1),
                             (-1, 2), (-1, -2), (-2, 1), (-2, -1)]:
      r = self.location.row + r_delta
      c = self.location.col + c_delta
      if Location.in_range(r, c):
        piece = board.at_location(Location(r, c))
        if not piece or piece.color != self.color:
          rtn.append(board.move(self.location, Location(r, c)))
    return rtn

class Bishop(Piece):
  def __init__(self, location = Location(), color = Color.black):
    super(Bishop, self).__init__(location, color, 'Bishop', 'B' if color == Color.white else 'b')

  def legal_moves(self, board):
    rtn = []
    for r_delta, c_delta in [(1, 1), (1, -1), (-1, 1), (-1, -1)]:
      r = self.location.row + r_delta
      c = self.location.col + c_delta
      if Location.in_range(r, c):
        piece = board.at_location(Location(r, c))
        while not piece and Location.in_range(r, c):
          rtn.append(board.move(self.location, Location(r, c)))
          r += r_delta
          c += c_delta
          if Location.in_range(r, c):
            piece = board.at_location(Location(r, c))
          else:
            piece = None
        if piece and piece.color != self.color:
          rtn.append(board.move(self.location, Location(r, c)))
    return rtn

class Queen(Piece):
  def __init__(self, location = Location(), color = Color.black):
  	super(Queen, self).__init__(location, color, 'Queen', 'Q' if color == Color.white else 'q')

  def legal_moves(self, board):
    rtn = []
    for r_delta, c_delta in [(0, 1), (0, -1), (1, 0), (-1, 0), (1, 1), (1, -1),
                             (-1, 1), (-1, -1)]:
      r = self.location.row + r_delta
      c = self.location.col + c_delta
      if Location.in_range(r, c):
        piece = board.at_location(Location(r, c))
        while not piece and Location.in_range(r, c):
          rtn.append(board.move(self.location, Location(r, c)))
          r += r_delta
          c += c_delta
          if Location.in_range(r, c):
            piece = board.at_location(Location(r, c))
          else:
            piece = None
        if piece and piece.color != self.color:
          rtn.append(board.move(self.location, Location(r, c)))
    return rtn

class King(Piece):
  def __init__(self, location = Location(), color = Color.black):
  	super(King, self).__init__(location, color, 'King', 'K' if color == Color.white else 'k')

  def legal_moves(self, board):
    rtn = []
    for r_delta, c_delta in [(1, -1), (1, 0), (1, 1), (0, 1),
                             (-1, 1), (-1, 0), (-1, -1), (0, -1)]:
      r = self.location.row + r_delta
      c = self.location.col + c_delta
      if Location.in_range(r, c):
        piece = board.at_location(Location(r, c))
        if not piece or piece.color != self.color:
          new_board = board.move(self.location, Location(r, c))
          new_king = new_board.at_location(Location(r, c))
          if not new_king.in_check(new_board):
            rtn.append(new_board)
    # Castling TODO
    return rtn

  def in_check(self, board):
    """ Returns true if this king is in check.

    Contruct the moves of all oppenent pieces and see if king
    is stolen, if so return true (don't construct other king's moves,
    as that would infinite loop, instead check his position manually).
    """
    oppenent_pieces = [x for x in board.pieces if (x.color != self.color and
                                                   x.name != King.name)]
    moves = []
    for p in oppenent_pieces:
      moves.extend(p.legal_moves(board))

    for move in moves:
      if not len([1 for x in move.pieces if (x.color == self.color and
                                             x.name == King.name)]):
        return True

    # For experimentation it can be helpful to have 0 or multiple kings
    oppenent_kings = [x for x in board.pieces if (x.color != self.color and
                                                 x.name == King.name)]
    for oppenent_king in oppenent_kings:
      if (abs(oppenent_king.location.row - self.location.row) < 2 and
          abs(oppenent_king.location.col - self.location.col) < 2):
        return True
    
    return False

    

b = Board()
b.pieces = [King(Location(2, 1), Color.black),
            King(Location(0, 0), Color.white)]
p = b.at_location(Location(2, 1))
moves = p.legal_moves(b)
for move in moves:
  print move

unittest.main()
