"""
This is the script where the board environment object is defined, and the rules
not related to the movement of the pieces are defined.

"""

import numpy as np
import random
import time
import copy  # we need to use deepcopy for copying custom objects with nested iterables.
from chess_pieces import *

random.seed(400)

# 1. Get board visualisation working
# 2. Get board updating working
# 3. Get pieces to choose from moves and take allowed moves


file = ["a", "b", "c", "d", "e", "f", "g", "h"]
rank = [1, 2, 3, 4, 5, 6, 7, 8]
file_dict = {file[i]: rank[i] for i in range(len(rank))}
file_dict_inv = {rank[i]: file[i] for i in range(len(rank))}
board = [(i, j) for i in file for j in rank]
castle_rank = {0: 1, 1: 8}  # rank each side castles on.


class ChessBoard:
    def __init__(self):
        self.square_info = {"piece": Piece(color=None), "control": None}
        self.active_pieces = [] # pieces currently in action TODO: modify this when queening
        self.initialize_board()
        self.turn = 0 # turn counter
        self.graveyard = [] # list containing pieces that were captured.
        self.current_player = 0
        self.perspective = 0  # perspective used when printing the board.
        self.game_end = False # flag if game has finished.
        self.move_log = {} # record of all moves played.
        self.game_result = None # the result of the game (1: white win, 0.5, draw, -1 black win)

    def play_game(self, n_turns=5, perspective=0, wait=0.5):
        # TODO: make this a while loop until game finished.
        self.perspective = perspective
        for i in range(n_turns):
            if self.game_end is False:
                print("white turn " + str(i))
                time.sleep(wait)
                self.take_turn()
                print("black turn " + str(i))
                time.sleep(wait)
                self.take_turn()
            else:
                print("Checkmate?")
                break

    def take_turn(self):
        """ - The current player takes a turn. The allowed moves are calculated.
            - The moves are iteratively tested in case they would put the king into
              check, in which case they are discarded.
            - If no candidate moves remain, then it must be checkmate or stalemate.
        """
        if self.turn % 2 == 0:
            self.current_player = 0
        else:
            self.current_player = 1

        allowed_moves = self.get_all_allowed_moves(self.board, self.current_player)

        legal = False
        while not legal:

            test_move = random.choice(allowed_moves)
            print(test_move)
            legal = self.try_update_board(test_move[0], test_move[1], self.current_player)
            if legal is False:  # if the move was illegal, remove it from candidates
                allowed_moves.remove(test_move)
            if len(allowed_moves) == 0:
                self.game_end = True
                print("NO LEGAL MOVES")
                self.print_board()
                self.print_board("control")
                print("^")
                break

        self.check_game_finished(allowed_moves)

        if self.game_end is False:
            piece = self.board[test_move[0]]["piece"]
            self.move_log[self.turn] = [self.current_player, piece.label, test_move[0], test_move[1]]
            self.update_board(test_move[0], test_move[1])
            self.board = self.update_board_control(self.board)
            self.turn += 1

        self.print_board()
        self.print_board("control")

    def check_game_finished(self, allowed_moves):
        """
        Check state of the board for win conditions.
        """
        # stalemate by 2 kings
        if len(self.graveyard) == 30:
            print("stalemate by 2 kings left")
            self.game_end = True
            self.game_result = 0.5

        # check for white victory
        if len(allowed_moves) == 0 and self.current_player == 1:
            for square in self.board:
                if self.board[square]["piece"].label == "K" and self.board[square]["piece"].color == 1:
                    if self.board[square]["control"] in [0, 2]:
                        print("Black is Checkmated!")
                        self.game_end = True
                        self.game_result = 1
                    else:
                        print("Something's wrong...")

        # check for black victory
        if len(allowed_moves) == 0 and self.current_player == 0:
            for square in self.board:
                if self.board[square]["piece"].label == "K" and self.board[square]["piece"].color == 0:
                    if self.board[square]["control"] in [1, 2]:
                        print("White is Checkmated!")
                        self.game_end = True
                        self.game_result = -1
                    else:
                        print("Something's wrong...")

    def initialize_board(self):
        """Set up the board in the standard chess configuration.
           TODO: Load setup from a config file to allow custom layouts.
        """
        board_positions = [(i, j) for i in file for j in rank]
        self.board = {k: self.square_info.copy() for k in board_positions}
        for ff in file:
            self.board[(ff, 2)]["piece"] = Pawn(color=0, position=(ff, 2))
            self.board[(ff, 7)]["piece"] = Pawn(color=1, position=(ff, 7))

        self.board[("e", 1)]["piece"] = King(color=0, position=("e", 1))
        self.board[("d", 1)]["piece"] = Queen(color=0, position=("d", 1))
        self.board[("e", 8)]["piece"] = King(color=1, position=("e", 8))
        self.board[("d", 8)]["piece"] = Queen(color=1, position=("d", 8))

        bishops = [[("c", 1), 0], [("f", 1), 0], [("c", 8), 1], [("f", 8), 1]]
        for i in bishops:
            self.board[i[0]]["piece"] = Bishop(color=i[1], position=i[0])

        knights = [[("b", 1), 0], [("g", 1), 0], [("b", 8), 1], [("g", 8), 1]]
        for i in knights:
            self.board[i[0]]["piece"] = Knight(color=i[1], position=i[0])

        rooks = [[("a", 1), 0], [("h", 1), 0], [("a", 8), 1], [("h", 8), 1]]
        for i in rooks:
            self.board[i[0]]["piece"] = Rook(color=i[1], position=i[0])

        self.board = self.update_board_control(self.board)

        for square in self.board:
            piece = self.board[square]["piece"]
            if piece.label != "O":
                self.active_pieces.append(piece)


    def print_color(self, text, piece_color, square_color=None):
        """Print the board out in colors depending on piece color
            CRED sets the colour to print, then CEND sets it back to white as usual.
        """
        if piece_color == 0:
            CRED = '\033[35m'

        elif piece_color == 1:
            CRED = '\033[33m'

        else:
            CRED = '\033[0m'

        CEND = '\033[0m'
        print(CRED + text + CEND, end="")

    def update_board(self, start_square, end_square):
        """Once a move has been selected, update the board."""
        # move the piece
        if end_square not in ["O-O", "O-O-O"]:
            if self.board[end_square]["piece"].label != "O":
                self.graveyard.append(self.board[end_square]["piece"])
                self.active_pieces.remove(self.board[end_square]["piece"])
            square_info = self.board[start_square].copy()
            square_info["piece"].position = end_square

            self.board[start_square] = {"piece": Piece(color=None), "control": None}
            self.board[end_square] = square_info
            self.board[end_square]["piece"].n_moves += 1

        # Implement special castling rules:
        elif start_square in [("e",1), ("e",8)] and end_square in ["O-O", "O-O-O"]:
            r = start_square[1]
            # Move king off stating square
            king_info = self.board[start_square].copy()
            self.board[start_square] = {"piece": Piece(color=None), "control": None}
            if end_square == "O-O":
                rook_info = self.board[("h", r)].copy()
                self.board[("h",r)] = {"piece": Piece(color=None), "control": None}
                self.board[("g",r)] = king_info
                self.board[("f", r)] = rook_info
                self.board[("g",r)]["piece"].n_moves += 1
                self.board[("f", r)]["piece"].n_moves += 1
            elif end_square == "O-O-O":
                rook_info = self.board[("a", r)].copy()
                self.board[("a",r)] = {"piece": Piece(color=None), "control": None}
                self.board[("c", r)] = king_info
                self.board[("d", r)] = rook_info
                self.board[("c", r)]["piece"].n_moves += 1
                self.board[("d", r)]["piece"].n_moves += 1
            else:
                print("Invalid castling?!")
            # Implement castling rules!

        # reassess the square control of the board

    def try_update_board(self, start_square, end_square, current_player):
        """Instead of updating the main board, make a copy to evaluate - used to see
           if a move is legal (doesn't put a king in check)"""
        # move the piece
        enemy_player = abs(1 - current_player)

        # Since castling is only allowed if king not in check, by default if
        # passed to this method as an argument, it is already allowed and would
        # not result in putting the king in check.
        if end_square in ["O-O", "O-O-O"]:
            allowed = True

        else:
            temp_board = copy.deepcopy(self.board)
            square_info = temp_board[start_square]
            square_info["piece"].position = end_square

            temp_board[start_square] = {"piece": Piece(color=None), "control": None}
            temp_board[end_square] = square_info
            temp_board = self.update_board_control(temp_board)

            allowed = True
            for square, attributes in temp_board.items():  # check if move has kept / put king in check
                if attributes["piece"].label == "K" and attributes["piece"].color == current_player:
                    if attributes["control"] in [enemy_player, 2]:
                        allowed = False

        return (allowed)

    def get_controlled_squares(self, board, current_player):
        """For a given piece at a given position, return the squares it controls."""
        controlled_squares = []
        for square in board:
            piece = board[square]["piece"]
            if piece.label != "O" and piece.color == current_player:
                _, control = piece.get_possible_moves(board, current_player)
                for c in control:
                    controlled_squares.append(c)
        if piece.label == "K":
            print(piece.label, piece.color, set(controlled_squares))

        return (set(controlled_squares))

    def update_board_control(self, board):
        """Take in the current position of all the pieces on the board
           and update the control overlay of the board (used to determine if
           either king is in check and thier valid moves)."""
        white_control = self.get_controlled_squares(board, 0)
        black_control = self.get_controlled_squares(board, 1)

        # reset board control to None before recalculating.
        for sq in board:
            board[sq]["control"] = None

        for w in white_control:
            if board[w]["control"] is None:
                board[w]["control"] = 0
            elif board[w]["control"] == 1:
                board[w]["control"] = 2
        for b in black_control:
            if board[b]["control"] is None:
                board[b]["control"] = 1
            elif board[b]["control"] == 0:
                board[b]["control"] = 2

        return (board)

    def get_all_allowed_moves(self, board, current_player):
        """For a given player (white or black), get all the possible moves they
           could make and return as a list. """
        moves = []
        enemy_player = abs(1 - current_player)

        for square in board:
            piece = board[square]["piece"]
            if piece.label != "O" and piece.color == current_player:
                possible_moves, _ = piece.get_possible_moves(board, current_player)
                for m in possible_moves:
                    moves.append((square, m))

        # conditions to be met to allow kingside castling
        r = castle_rank[current_player]
        kingside = [board[("e", r)]["piece"].label == "K",  # king is on starting square
                    board[("e", r)]["piece"].n_moves == 0,  # king hasn't moved
                    board[("h", r)]["piece"].label == "R",  # rook on starting square
                    board[("h", r)]["piece"].n_moves == 0,  # rook hasn't moved
                    board[("e", r)]["control"] not in [enemy_player, 2],  # king not in check
                    board[("f", r)]["control"] not in [enemy_player, 2],  # f1 not in check
                    board[("g", r)]["control"] not in [enemy_player, 2],  # g1 not in check
                    board[("f", r)]["piece"].label == "O",  # f1 clear of any pieces
                    board[("g", r)]["piece"].label == "O",  # g1 clear of any pieces
                    ]
        # conditions to be met to allow queenside castling
        queenside = [board[("e", r)]["piece"].label == "K",  # king is on starting square
                     board[("e", r)]["piece"].n_moves == 0,  # king hasn't moved
                     board[("a", r)]["piece"].label == "R",  # rook on starting square
                     board[("a", r)]["piece"].n_moves == 0,  # rook hasn't moved
                     board[("e", r)]["control"] not in [enemy_player, 2],  # king not in check
                     board[("d", r)]["control"] not in [enemy_player, 2],  # d1 not in check
                     board[("c", r)]["control"] not in [enemy_player, 2],  # c1 not in check
                     board[("b", r)]["control"] not in [enemy_player, 2],  # b1 not in check
                     board[("d", r)]["piece"].label == "O",  # d1 clear of any pieces
                     board[("c", r)]["piece"].label == "O",  # c1 clear of any pieces
                     board[("b", r)]["piece"].label == "O",  # b1 clear of any pieces
                     ]

        # If all conditions for kingside castling are met:
        if all(kingside):
            moves.append((("e",r), "O-O"))

        # If all conditions for queenside castling are met:
        if all(queenside):
            moves.append((("e",r), "O-O-O"))

        return (moves)

    def print_board(self, scheme="pieces"):
        """Print out the state of the board.
           if scheme - "control", print out the control overlay of the board."""
        self.print_color("white", 0), print(" ")
        self.print_color("black", 1), print("")
        sp = " "
        print(" ", end=sp)
        rank_r = rank.copy()
        file_r = file.copy()
        if self.perspective == 0:
            rank_r.reverse()
        elif self.perspective == 1:
            file_r.reverse()
        for ff in file_r:
            print(ff, end=sp)

        for rr in rank_r:
            print(sp)
            for ff in file_r:
                if ff == "a" and self.perspective == 0:
                    print(rr, end=sp)
                elif ff == "h" and self.perspective == 1:
                    print(rr, end=sp)
                piece = self.board[(ff, rr)]["piece"]
                value = piece.label
                if scheme == "control":
                    value = self.board[(ff, rr)]["control"]
                    if value is None: value = " "

                self.print_color(str(value) + sp, piece.color)
        print(" \n ")

    def print_move_log(self):
        """Print the moves played by each side in a game."""
        for i in range(len(self.move_log)):
            print(i, self.move_log[i])


# = King()

# print(K.get_possible_moves))
cb = ChessBoard()
cb.print_board()
cb.perspective = 0
cb.print_board("control")

# cb.board
#cb.update_board(("f", 8), ("f", 5))
#cb.update_board(("g", 8), ("g", 5))
#cb.update_board(("d", 8), ("d", 5))
#cb.update_board(("b", 8), ("b", 5))
#cb.update_board(("c", 8), ("c", 5))
#cb.update_board(("e",8), "O-O")

#cb.board = cb.update_board_control(cb.board)

cb.print_board("control")

cb.play_game(500, perspective=0, wait=0)
print(len(cb.active_pieces))
print((cb.active_pieces))