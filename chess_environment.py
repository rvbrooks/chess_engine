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
        self.initialize_board()
        self.turn = 0
        self.graveyard = []
        self.current_player = 0
        self.perspective = 0
        self.game_end = False
        self.move_log = {}
        self.game_result = None

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

    def print_move_log(self):
        for i in range(len(self.move_log)):
            print(i, self.move_log[i])

    def take_turn(self):
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
                self.print_board_control()
                print("^")
                break

        self.check_game_finished()

        if self.game_end is False:
            piece = self.board[test_move[0]]["piece"]
            self.move_log[self.turn] = [self.current_player, piece.label, test_move[0], test_move[1]]
            self.update_board(test_move[0], test_move[1])
            self.board = self.update_board_control(self.board)
            self.turn += 1

        self.print_board()
        # self.print_board_control()

    def check_game_finished(self):
        """
        Check state of the board for win conditions.
        """
        # stalemate by 2 kings
        if len(self.graveyard) == 30:
            print("stalemate by 2 kings left")
            self.game_end = True
            self.game_result = 0.5

    def initialize_board(self):
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

    def print_board(self):
        """Print out the current state of the board
           TODO: save past states of a given game and print them out move by move
           (with an evaluation?)"""
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
                l = self.board[(ff, rr)]["piece"]
                self.print_color(l.label + sp, l.color)
        print(" \n ")

    def print_board_control(self):
        """Print out the current state of the board
           TODO: save past states of a given game and print them out move by move
           (with an evaluation?)"""
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
                l = self.board[(ff, rr)]["piece"]
                c = self.board[(ff, rr)]["control"]

                if c is None:
                    c = " "
                self.print_color(str(c) + sp, l.color)
        print(" \n ")

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
        # move the piece
        if start_square not in ["O-O", "O-O-O"]
            if self.board[end_square]["piece"].label != "O":
                self.graveyard.append(self.board[end_square]["piece"])
            square_info = self.board[start_square].copy()
            square_info["piece"].position = end_square

            self.board[start_square] = {"piece": Piece(color=None), "control": None}
            self.board[end_square] = square_info
            self.board[end_square]["piece"].n_moves += 1

        elif start_square == "O-O" or start_square == "O-O-O":
            pass
            # Implement castling rules!

        # reassess the square control of the board

    def try_update_board(self, start_square, end_square, current_player):
        """Instead of updating the main board, make a copy to evaluate - used to see
           if a move is legal (doesn't put a king in check)"""
        # move the piece
        enemy_player = abs(1 - current_player)

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
            moves.append(("O-O", "O-O"))

        # If all conditions for queenside castling are met:
        if all(queenside):
            moves.append("O-O-O", "O-O-O")

        return (moves)


# = King()

# print(K.get_possible_moves))
cb = ChessBoard()
cb.print_board()
cb.perspective = 0
cb.print_board_control()

# cb.board
cb.update_board(("f", 1), ("f", 5))
cb.update_board(("g", 1), ("g", 5))
cb.update_board(("e", 1), ("f", 1))
cb.update_board(("f", 1), ("e", 1))
cb.update_board(("h", 1), ("f", 1))
cb.update_board(("f", 1), ("c", 5))
cb.update_board(("d", 8), ("g", 2))
cb.board = cb.update_board_control(cb.board)

cb.print_board()

a = cb.get_all_allowed_moves(cb.board, 0)
print(a)

# cb.play_game(1, perspective=0, wait=0)
