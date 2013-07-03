class Location(object):
  row_range = range(8)
  col_range = range(8)

  def __init__(self, row = 0, col = 0):
    if row not in self.row_range or col not in self.col_range:
  	  raise Exception('Illegal location ' + str(row) + ', ' + str(col))
    self.row = row
    self.col = col

  @classmethod
  def in_range(cls, row, col):
    return row in cls.row_range and col in cls.col_range

  def __eq__(self, other_location):
    return self.row == other_location.row and self.col == other_location.col

  def __str__(self):
    return str(self.row) + ', ' + str(self.col)

class Color(object):
  black = 'BLACK'
  white = 'WHITE'

  @staticmethod
  def opposite(clr):
    if clr == Color.black:
      return Color.white
    return Color.black

class Piece(object):
  def __init__(self, location = Location(), color = Color.black,
               name = 'DEFAULT', letter = 'D'):
    self.location = location
    self.color = color
    self.name = name
    self.letter = letter
    self.move_count = 0

  def legal_moves(self, board):
    return []

  def copy(self):
    p = self.__class__()
    p.color = self.color
    p.name = self.name
    p.letter = self.letter
    p.location = Location(self.location.row, self.location.col)
    p.move_count = self.move_count
    return p

  def direction(self):
    """
    White starts at the 0th row and moves toward the 7th row, so
    it is +1, Black starts at the 7th and moves toward 0th so it is -1.
    """
    return 1 if self.color == Color.white else -1 

  def row(self, x):
    """
    Normalizes rows for white versus black, so x is the number of rows from
    the starting side, and the row returned is the actual index into the
    board.
    e.x. If it is a white piece row(1) returns 1 because 1 is the second row
    on the white side.
    If it is a black piece row(1) returns 6 because 6 is the second row on the
    black side.
    """
    direction = self.direction()
    if direction == 1:
      return x
    else:
      return 7 - x


  def __str__(self):
    return self.color + ' ' + self.name + ' at ' + str(self.location)

  def __eq__(self, p):
    return (self.color == p.color and self.name == p.name and
            self.letter == p.letter and self.location == p.location)
      
class Board(object):
  def __init__(self):
    self.turn = Color.white
    self.pieces = self.reset_pieces()
    self.history = []

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
    move_piece = new_board.at_location(start_location)
    move_piece.move_count += 1
    move_piece.location = end_location
    # Update turn and piece history
    new_board.turn = Color.opposite(self.turn)
    new_board.history.append(self.pieces)
    return new_board

  def copy(self):
    rtn = Board()
    rtn.pieces = []
    rtn.turn = self.turn
    rtn.history = self.history
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

class Pawn(Piece):
  def __init__(self, location = Location(), color = Color.black):
    super(Pawn, self).__init__(location, color, 'Pawn', 'P' if color == Color.white else 'p')

  def legal_moves(self, board):
    rtn = []
    col = self.location.col
    # First move can go two
    if (self.location.row == self.row(1) and
        not board.at_location(Location(self.row(2),col)) and
        not board.at_location(Location(self.row(3),col))):
      rtn.append(board.move(self.location, Location(self.row(3), col)))
    # Move forward one
    row = self.location.row + self.direction()
    col = self.location.col
    if (Location.in_range(row, col) and
        not board.at_location(Location(row, col))):
      if row != self.row(7):
        rtn.append(board.move(self.location, Location(row, col)))
      else:
        rtn.extend(self.pawn_upgrade(board, self.location,
                                     Location(row, col)))
    # Captures
    for col_delta in [-1, 1]:
      col = self.location.col + col_delta 
      if Location.in_range(row, col):
        capture_piece = board.at_location(Location(row, col))
        if capture_piece and capture_piece.color != self.color:
          if row != self.row(7):
            rtn.append(board.move(self.location,
                                  Location(row, col)))
          else:
            rtn.extend(self.pawn_upgrade(board, self.location,
                                         Location(row, col)))
      # En Passant
      if self.location.row == self.row(4):
        piece = board.at_location(Location(self.location.row, col))
        if piece.name == Pawn.name and piece.move_count == 1:
          new_board = board.move(self.location, Location(row, col))
          captured_piece = new_board.at_location(Location(self.location.row, col))
          new_board.piece.remove(captured_piece)
          rtn.append(new_board) 
    return rtn

  def pawn_upgrade(self, board, old_location, new_location):
    rtn = []
    for piece in [Pawn, Bishop, Rook, Knight, Queen]:
      new_board = board.move(old_location, new_location)
      new_piece = new_board.at_location(new_location)
      new_board.pieces.remove(new_piece)
      new_board.pieces.append(piece(Location(new_location)))
      rtn.append(new_board)
    return rtn

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
    # Castling (TODO)
    #if self.move_count == 0:
    #  for loc in [Location(self.row(0),0), Location(self.row(0),7)]:
        
    return rtn

  def in_check(self, board):
    """ Returns true if this king is in check.

    Contruct the moves of all oppenent pieces and see if king
    is stolen, if so return true (don't construct other king's moves,
    as that would infinite loop, instead check his position manually).
    """
    oppenent_pieces = [x for x in board.pieces if (x.color != self.color and
                                                   x.name != self.name)]
    moves = []
    for p in oppenent_pieces:
      moves.extend(p.legal_moves(board))

    for move in moves:
      if not len([1 for x in move.pieces if (x.color == self.color and
                                             x.name == self.name)]):
        return True

    # For experimentation it can be helpful to have 0 or multiple kings
    oppenent_kings = [x for x in board.pieces if (x.color != self.color and
                                                 x.name == self.name)]
    for oppenent_king in oppenent_kings:
      if (abs(oppenent_king.location.row - self.location.row) < 2 and
          abs(oppenent_king.location.col - self.location.col) < 2):
        return True
    
    return False

if __name__ == "__main__":
  b = Board()
  b.pieces = [King(Location(2, 1), Color.black),
              King(Location(0, 0), Color.white)]
  p = b.at_location(Location(2, 1))
  moves = p.legal_moves(b)
  for move in moves:
    print move

