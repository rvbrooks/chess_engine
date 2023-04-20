"""
This is the script where the board environment object is defined, and the rules
not related to the movement of the pieces are defined.

"""
import os
import random
import time
import copy  # we need to use deepcopy for copying custom objects with nested iterables.
from chess_pieces import Piece, King, Queen, Rook, Bishop, Knight, Pawn
random.seed(3) # 3005, 67436: black checkmates white; 3: white checkmates black

# 1. Get board visualisation working
# 2. Get board updating working
# 3. Get pieces to choose from moves and take allowed moves


file = ["a", "b", "c", "d", "e", "f", "g", "h"]
rank = [1, 2, 3, 4, 5, 6, 7, 8]
file_dict = {file[i]: rank[i] for i in range(len(rank))}  # letter:number
file_dict_inv = {rank[i]: file[i] for i in range(len(rank))}  # numer:letter
#board = [(i, j) for i in file for j in rank]
castle_rank = {0: 1, 1: 8}  # rank each side castles on.
available_pieces = {"K": King, "Q": Queen, "R": Rook, "B": Bishop, "N": Knight, "P": Pawn}
color_encoding = {0:"white", 1:"black"}


class ChessBoard:
    def __init__(self):
        self.board = {}
        self.empty_square_info = {"piece": Piece(color=None), "control": None}
        self.active_pieces = []  # pieces currently in action TODO: modify this when queening
        self.perspective = 0  # perspective used when printing the board.
        self.initialize_board()
        self.turn = 0  # turn counter
        self.graveyard = []  # list containing pieces that were captured.
        self.current_player = 0
        self.game_end = False  # flag if game has finished.
        self.move_log = {}  # record of all moves played.
        self.game_result = None  # the result of the game (1: white win, 0.5, draw, -1 black win)

    def play_game(self, n_turns=5, perspective=0, wait=0.5):
        # TODO: make this a while loop until game finished.
        self.perspective = perspective
        for i in range(n_turns):
            if self.game_end is False:
                print("white turn " + str(i))
                time.sleep(wait)
                self.take_turn()
            if self.game_end is False:
                print("black turn " + str(i))
                time.sleep(wait)
                self.take_turn()
            else:
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
                print("Final board position:")
                break

        self.check_game_finished(allowed_moves)

        if self.game_end is False:
            # if not a pawn promotion move:
            if len(test_move[1]) == 2:
                self.update_board(test_move[0], test_move[1])
            # elif instead a pawn promtion move
            else:
                end_square = (test_move[1][0], test_move[1][1])
                self.update_board(test_move[0], end_square, test_move[1][2])

            self.board = self.update_board_control(self.board)

        self.print_board()
        self.print_board("control")

    def check_game_finished(self, allowed_moves):
        """
        Check state of the board for won/lose/draw conditions.
        1. One side checkmates the other
        2. Draw if one side traps other king with no moves left but not in check
        3. Draw if stalemate from only 2 kings left
        4. Draw if stalemate from only 2 kings and bishop/knight left (insufficient for checkmate)
        TODO: implement draw by repetition and by 50 moves no captures.
        """
        # stalemate by 2 kings

        # Check for checkmate and stalemate.
        if len(allowed_moves) == 0:
            enemy_player = abs(1 - self.current_player)
            for square in self.board:
                if self.board[square]["piece"].label == "K" and self.board[square]["piece"].color == self.current_player:
                    if self.board[square]["control"] in [enemy_player, 2]:
                        print(color_encoding[self.current_player]+" is Checkmated!")
                        self.game_end = True
                        if self.current_player == 0:
                            self.game_result = 1
                        elif self.current_player == 1:
                            self.game_result = -1
                    elif self.board[square]["control"] not in [enemy_player, 2]:
                        print(color_encoding[self.current_player]+" is Stalemated!")
                        self.game_end = True
                        self.game_result = 0.5
                    else:
                        print("Something's wrong...")

        elif len(self.graveyard) == 30:
            print("stalemate by 2 kings left")
            self.game_end = True
            self.game_result = 0.5

        elif len(self.graveyard) == 29:
            for piece in self.active_pieces:
                if piece.label in ["B", "N"]:
                    print("stalemate by 2 kings & bishop/knight left")
                    self.game_end = True
                    self.game_result = 0.5

        elif len(self.graveyard) == 28:
            w, b = [], []
            for piece in self.active_pieces:
                if piece.color == 0:
                    w.append(piece.label)
                elif piece.color == 1:
                    b.append(piece.label)
                if len(w) == len(b):
                    if "Q" not in [w, b] and "R" not in [w, b]:
                        print("stalemate by 2 kings & bishop/knight each left")
                        self.game_end = True
                        self.game_result = 0.5

    def initialize_board(self, filename="default_board_config.txt"):
        pwd = os.path.dirname(__file__).rsplit('\\', 1)[0]+"\\board_configs\\"
        configname = pwd + filename
        board_positions = [(i, j) for i in file for j in rank]
        self.board = {k: self.empty_square_info.copy() for k in board_positions}
        with open(configname, "r") as open_file:
            for line in open_file:
                print(line)
                color, piece, ff, rr = line.split(";")
                position = (ff, int(rr))
                self.board[position]["piece"] = available_pieces[piece](color=int(color), position=position)

        self.board = self.update_board_control(self.board)

        for square in self.board:
            piece = self.board[square]["piece"]
            if piece.label != "O":
                self.active_pieces.append(piece)

        self.print_board()
        self.print_board("control")



    def update_board(self, start_square, end_square, promotion=None):
        """Once a move has been selected, update the board. Checks for special moves through
            if statements:
            1. If normal move?
            2. If castling move?
            3. If en-passant move?
            4. If pawn promotion move?
        """
        # update the move log
        piece = self.board[start_square]["piece"]
        self.move_log[self.turn] = [self.current_player, piece.label, start_square, end_square]

        # Basic piece movement
        if end_square not in ["O-O", "O-O-O", "EP_kingside", "EP_queenside"] and promotion is None:
            if self.board[end_square]["piece"].label != "O":
                self.graveyard.append(self.board[end_square]["piece"])
                self.active_pieces.remove(self.board[end_square]["piece"])
            square_info = self.board[start_square].copy()
            square_info["piece"].position = end_square

            self.board[start_square] = self.empty_square_info.copy()
            self.board[end_square] = square_info
            self.board[end_square]["piece"].n_moves += 1

        # Implement special castling rules:
        elif start_square in [("e", 1), ("e", 8)] and end_square in ["O-O", "O-O-O"]:
            self.board = self.perform_castling(self.board, start_square, end_square)

        # implement special en-passant rules
        elif end_square in ["EP_kingside", "EP_queenside"]:
            self.board, captured_square = self.perform_en_passant(self.board, start_square, end_square)
            self.graveyard.append(self.board[captured_square]["piece"])
            self.active_pieces.remove(self.board[captured_square]["piece"])

        # implement special pawn promotion rules
        elif promotion in ["Q", "R", "B", "N"]:
            if self.board[end_square]["piece"].label != "O":
                self.graveyard.append(self.board[end_square]["piece"])
                self.active_pieces.remove(self.board[end_square]["piece"])
            self.board = self.perform_pawn_promotion(self.board, start_square, end_square, promotion)
            self.active_pieces.append(self.board[end_square]["piece"])

        self.turn += 1

    def try_update_board(self, start_square, end_square, current_player, promotion=None):
        """Instead of updating the main board, make a copy to evaluate - used to see
           if a move is legal (doesn't put a king in check)
           FIXME: Need to implement the special rules in the try update!!
           """
        # move the piece
        enemy_player = abs(1 - current_player)
        temp_board = copy.deepcopy(self.board)

        if end_square not in ["O-O", "O-O-O", "EP_kingside", "EP_queenside"] and promotion is None:

            square_info = temp_board[start_square]
            square_info["piece"].position = end_square
            temp_board[start_square] = self.empty_square_info.copy()
            temp_board[end_square] = square_info
            temp_board = self.update_board_control(temp_board)

        elif end_square in ["O-O", "O-O-O"]:  # already checked that castling is legal.
            temp_board = self.perform_castling(temp_board, start_square, end_square)

        elif end_square in ["EP_kingside", "EP_queenside"]:
            temp_board, captured_square = self.perform_en_passant(temp_board, start_square, end_square)

        elif promotion in ["Q", "R", "B", "N"]:
            temp_board = self.perform_pawn_promotion(temp_board, start_square, end_square, promotion)

        for square, attributes in temp_board.items():  # check if move has kept / put king in check
            if attributes["piece"].label == "K" and attributes["piece"].color == current_player:
                if attributes["control"] in [enemy_player, 2]: # if king in check after this move
                    allowed = False
                else:  # if king not in check after this move:
                    allowed = True
        return (allowed)

    def perform_castling(self, board, start_square, end_square):
        """Update the board according to special castling rules.
           Implemented as a separate method to update_board so that it can be called from
           try_update_board.
           Inputs:
                - board dictionary object
                - start_square: tuple of the initial square
                - end_square: string flag for perform castling (O-O or O-O-O)
            Outputs:
                - updated board object
        """
        r = start_square[1]
        # Move king off stating square
        king_info = board[start_square].copy()
        board[start_square] = self.empty_square_info.copy()
        if end_square == "O-O":
            rook_info = board[("h", r)].copy()
            board[("h", r)] = self.empty_square_info.copy()
            board[("g", r)] = king_info
            board[("f", r)] = rook_info
            board[("g", r)]["piece"].n_moves += 1
            board[("f", r)]["piece"].n_moves += 1
        elif end_square == "O-O-O":
            rook_info = board[("a", r)].copy()
            board[("a", r)] = self.empty_square_info.copy()
            board[("c", r)] = king_info
            board[("d", r)] = rook_info
            board[("c", r)]["piece"].n_moves += 1
            board[("d", r)]["piece"].n_moves += 1
        else:
            print("Invalid castling?!")
        return (board)

    def perform_en_passant(self, board, start_square, end_square):
        """Update the board according to special en-passant rules.
           Implemented as a separate method to update_board so that it can be called from
           try_update_board.
           Inputs:
                - board dictionary object
                - start_square: tuple of the initial square
                - end_square: string flag for perform castling (EP_kingside / EP_queenside)
            Outputs:
                - updated board object
        """
        if self.current_player == 0:
            s = 1
        elif self.current_player == 1:
            s = -1
        square_info = board[start_square].copy()

        board[start_square] = self.empty_square_info.copy()
        if end_square == "EP_kingside":
            end_square = (file_dict_inv[file_dict[start_square[0]] + 1], start_square[1] + 1 * s)
            captured_square = (file_dict_inv[file_dict[start_square[0]] + 1], start_square[1])
        elif end_square == "EP_queenside":
            end_square = (file_dict_inv[file_dict[start_square[0]] - 1], start_square[1] + 1 * s)
            captured_square = (file_dict_inv[file_dict[start_square[0]] - 1], start_square[1])

        # remove the capture en-passant pawn to the graveyard

        board[captured_square] = self.empty_square_info.copy()

        # move the capturing pawn to the final square
        square_info["piece"].position = end_square
        board[end_square] = square_info
        board[end_square]["piece"].n_moves += 1

        return (board, captured_square)

    def perform_pawn_promotion(self, board, start_square, end_square, promotion):
        """Update the board according to special pawn promotion rules.
                   Implemented as a separate method to update_board so that it can be called from
                   try_update_board.
                   Inputs:
                        - board dictionary object
                        - start_square: tuple of the initial square
                        - end_square: square to promote on
                        - promotion: choice of piece to promote to.
                    Outputs:
                        - updated board object
                """
        square_info = board[start_square].copy()
        square_info["piece"].position = copy.copy(end_square)

        board[start_square] = self.empty_square_info.copy()
        P = available_pieces[promotion]

        new_piece = P(color=self.current_player, position=end_square)
        print(new_piece)

        board[end_square]["piece"] = new_piece
        return (board)

    def get_controlled_squares(self, board, current_player):
        """For a given piece at a given position, return the squares it controls.
           Inputs:
            - board: board dictionary object necessary to determine collisions
            - current_player: integer

            """
        controlled_squares = []
        for square in board:
            piece = board[square]["piece"]
            if piece.label != "O" and piece.color == current_player:
                _, control = piece.get_possible_moves(board, current_player)
                for c in control:
                    controlled_squares.append(c)

        return (set(controlled_squares))

    def update_board_control(self, board):
        """Take in the current position of all the pieces on the board
           and update the control overlay of the board (used to determine if
           either king is in check and their valid moves)."""
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

        # EN-PASSANT
        if len(self.move_log) > 2:
            ml = self.move_log[self.turn - 1]  # check the last move if it was a double pawn move
            if ml[1] == "P" and ml[0] == enemy_player and type(ml[3]) != str:
                # if opponent pawn's last move was to move 2
                if abs(ml[2][1] - ml[3][1]) == 2:
                    f_end, r_end = ml[3]
                    if file_dict[f_end] - 1 in rank:
                        nf = file_dict_inv[file_dict[f_end] - 1]
                        if board[(nf, r_end)]["piece"].label == "P" and \
                                board[(nf, r_end)]["piece"].color == current_player:
                            moves.append(((nf, r_end), "EP_kingside"))

                    if file_dict[f_end] + 1 in rank:
                        nf = file_dict_inv[file_dict[f_end] + 1]

                        if board[(nf, r_end)]["piece"].label == "P" and \
                                board[(nf, r_end)]["piece"].color == current_player:
                            moves.append(((nf, r_end), "EP_queenside"))

        # CASTLING
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
            moves.append((("e", r), "O-O"))

        # If all conditions for queenside castling are met:
        if all(queenside):
            moves.append((("e", r), "O-O-O"))

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

    def print_color(self, text, piece_color, square_color=None):
        """Print the board out in colors depending on piece color
            temp_color sets the colour to print, then base_color sets it back to white as usual.
        """
        if piece_color == 0:
            temp_color = '\033[35m'

        elif piece_color == 1:
            temp_color = '\033[33m'

        else:
            temp_color = '\033[0m'

        base_color = '\033[0m'
        print(temp_color + text + base_color, end="")

    def print_move_log(self):
        """Print the moves played by each side in a game."""
        for i in range(len(self.move_log)):
            print(i, self.move_log[i])


if __name__ == "__main__":
    cb = ChessBoard()
    cb.perspective = 0

    cb.play_game(500, perspective=0, wait=0)

