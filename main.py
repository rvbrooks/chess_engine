from chess_pieces import Piece, King, Queen, Rook, Bishop, Knight, Pawn
from chess_environment import ChessBoard

if __name__ == "__main__":
    cb = ChessBoard()
    cb.perspective = 0

    cb.play_game(500, perspective=0, wait=0)

