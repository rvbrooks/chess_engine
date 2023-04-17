import numpy as np
import random
random.seed()
import time
# How to organise board object?
# A board which contains Piece objects?

# 1. Get board visualisation working
# 2. Get board updating working
# 3. Get pieces to choose from moves and take allowed moves
# 4. Make special moves like en Peasant, castling and queening working
# 5. Make it play a totally random game of random moves.

file = ["a","b","c","d","e","f","g","h"]
rank = [1, 2, 3, 4, 5, 6, 7, 8]
file_dict = {file[i]:rank[i] for i in range(len(rank))}
file_dict_inv = {rank[i]:file[i] for i in range(len(rank))}
board = [(i, j) for i in file for j in rank]


# class Board, and a plot_board method.
# need board class to check where other pieces are?


class ChessBoard():
    def __init__(self):
        self.square_info = {"piece": Piece(color=None), "control":None}
        self.initialize_board()
        self.turn = 0
        self.graveyard = []
        self.current_player = 0
        self.perspective = 0
        self.game_end = False

    
    def play_game(self, n_turns = 5, perspective = 0, wait = 0.5):
        self.perspective = perspective
        for i in range(n_turns):
            if self.game_end == False:
                print("white turn "+str(i))
                time.sleep(wait)
                self.take_turn()
                print("black turn "+str(i))
                time.sleep(wait)
                self.take_turn()
            else:
                print("Checkmate?")
                break
        
    def take_turn(self):
        if self.turn % 2 == 0:
            self.current_player = 0
        else: 
            self.current_player = 1
        
        allowed_moves = self.get_all_allowed_moves(self.board, self.current_player)
        
        legal = False
        while legal == False:
            
            test_move = random.choice(allowed_moves)
            print(test_move)
            legal = self.try_update_board(test_move[0], test_move[1], self.current_player)
            if legal == False:
                allowed_moves.remove(test_move)
            if len(allowed_moves) == 0:
                if self.current_player == 0:
                    print("white in check")
                elif self.current_player == 1:
                    print("black in check")
                self.game_end = True
                break

        self.update_board(test_move[0], test_move[1])
        self.print_board()
        #self.print_board_control()
        
        self.turn += 1


    
    def initialize_board(self):
        board_positions = [(i, j) for i in file for j in rank]
        self.board = {k : self.square_info.copy() for k in board_positions}
        for ff in file:
            self.board[(ff, 2)]["piece"] = Pawn(color = 0, position = (ff, 2))
            self.board[(ff, 7)]["piece"] = Pawn(color = 1, position = (ff, 7))
            
        self.board[("e", 1)]["piece"] = King(color = 0, position = ("e", 1))
        self.board[("d", 1)]["piece"] = Queen(color = 0, position = ("d", 1))
        self.board[("e", 8)]["piece"] = King(color = 1, position = ("e", 8))
        self.board[("d", 8)]["piece"] = Queen(color = 1, position = ("d", 8))
        
        bishops = [[("c", 1), 0], [("f", 1), 0], [("c", 8), 1], [("f", 8), 1]]
        for i in bishops:
            self.board[i[0]]["piece"] = Bishop(color = i[1], position = i[0])
        
        knights = [[("b", 1), 0], [("g", 1), 0], [("b", 8), 1], [("g", 8), 1]]
        for i in knights:
            self.board[i[0]]["piece"] = Knight(color = i[1], position = i[0])
            
        rooks = [[("a", 1), 0], [("h", 1), 0], [("a", 8), 1], [("h", 8), 1]]
        for i in rooks:
            self.board[i[0]]["piece"] = Rook(color = i[1], position = i[0])
        
        self.board = self.update_board_control(self.board)
            

    def print_board(self):
        """Print out the current state of the board
           TODO: save past states of a given game and print them out move by move
           (with an evaluation?)"""
        self.print_color("white", 0), print(" ")
        self.print_color("black", 1), print("")
        sp = " "
        print(" ", end = sp)

        if self.perspective == 0:
            rank_r = rank.copy()
            rank_r.reverse()
            file_r = file.copy()
        elif self.perspective == 1:
            rank_r = rank
            file_r = file.copy()
            file_r.reverse()

        for ff in file_r:
            print(ff, end = sp)
            
        for rr in rank_r:
            print(sp)
            for ff in file_r:
                if ff == "a" and self.perspective == 0:
                    print(rr, end = sp)
                elif ff == "h" and self.perspective == 1:
                    print(rr, end = sp)
                L = self.board[(ff,rr)]["piece"]
                self.print_color(L.label+sp, L.color)
        print(" \n ")

    def print_board_control(self):
        """Print out the current state of the board
           TODO: save past states of a given game and print them out move by move
           (with an evaluation?)"""
        self.print_color("white", 0), print(" ")
        self.print_color("black", 1), print("")
        sp = " "
        print(" ", end = sp)

        if self.perspective == 0:
            rank_r = rank.copy()
            rank_r.reverse()
            file_r = file.copy()
        elif self.perspective == 1:
            rank_r = rank
            file_r = file.copy()
            file_r.reverse()

        for ff in file_r:
            print(ff, end = sp)
            
        for rr in rank_r:
            print(sp)
            for ff in file_r:
                if ff == "a" and self.perspective == 0:
                    print(rr, end = sp)
                elif ff == "h" and self.perspective == 1:
                    print(rr, end = sp)
                L = self.board[(ff, rr)]["piece"]
                C = self.board[(ff,rr)]["control"]

                if C is None:
                    C = " "
                self.print_color(str(C)+sp, L.color)
        print(" \n ")

    def print_color(self, text, piece_color, square_color = None):
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
        print(CRED+text+CEND, end = "")
    
    def update_board(self, start_square, end_square):
        # move the piece
        if self.board[end_square]["piece"].label != "O":
            self.graveyard.append(self.board[end_square]["piece"])
        square_info = self.board[start_square].copy()
        square_info["piece"].update_position(end_square)
        
        self.board[start_square] = {"piece": Piece(color=None), "control":None}
        self.board[end_square] = square_info
        # reassess the square control of the board
        self.board = self.update_board_control(self.board)

   
    def try_update_board(self, start_square, end_square, current_player):
        """Instead of updating the main board, make a copy to evaluate - used to see
           if a move is legal (doesn't put a king in check)"""
        # move the piece
        enemy_player = abs(1-current_player)
        
        
        
        temp_board = self.board.copy()
        square_info = temp_board[start_square]
        square_info["piece"].update_position(end_square)
        
        temp_board[start_square] = {"piece": Piece(color=None), "control":None}
        temp_board[end_square] = square_info
        temp_board = self.update_board_control(temp_board)
        
        allowed = True
        for square, attributes in temp_board.items(): # check if move has kept / put king in check
            if attributes["piece"].label == "K" and attributes["piece"].color == current_player:
                if attributes["control"] in [enemy_player, 2]:
                    allowed = False
        return(allowed)
        
    def get_controlled_squares(self, board, current_player):
        controlled_squares = []
        for square in board:
            piece = board[square]["piece"]
            if piece.label != "O" and piece.color == current_player:
                _, control = piece.get_possible_moves(board, current_player)
                for c in control:
                    controlled_squares.append(c)
        return(set(controlled_squares))
    
    def update_board_control(self, board):
        white_control = self.get_controlled_squares(board, 0)
        black_control = self.get_controlled_squares(board, 1)
        
        for s in board:
            board[s]["control"] = None

        for w in white_control:
            if board[w]["control"] == None:
                board[w]["control"] = 0
            elif board[w]["control"] == 1:
                board[w]["control"] = 2
        for b in black_control:
            if board[b]["control"] == None:
                board[b]["control"] = 1
            elif board[b]["control"] == 0:
                board[b]["control"] = 2

        return(board)

    def get_all_allowed_moves(self, board, current_player):
        moves = []
        for square in board:
            piece = board[square]["piece"]
            if piece.label != "O" and piece.color == current_player:
                possible_moves, _ = piece.get_possible_moves(board, current_player)
                for m in possible_moves:
                    moves.append((square, m))
        return(moves)                

class Piece():
    def __init__(self, color = 0, value = 0, position = (0,0)):
        self.value = value
        self.position = position
        self.color = color
        self.n_moves = 0
        self.label = "O"
    
    def __repr__(self):
        return(self.label)
    
    def get_label(self):
        return(self.label)
    
    def get_current_position(self):
        return(self.position)

    def update_position(self, new_position):
        self.position = new_position
    
    def get_possible_moves(self):
        """This is the possible moves that could be made given the type of piece
           but not yet accounting for if the space is occupied or not.  """

        possible_moves = []
        control = []
        
        return(possible_moves, control)
         
class King(Piece):
    def __init__(self, color=0, value=1000000, position=("d",1)):
        Piece.__init__(self, color, value, position)
        self.in_check = False
        self.label = "K"
    
    def get_possible_moves(self, board_state, current_player):
        ff = file_dict[self.position[0]]
        rr = self.position[1]
        possible_moves = []
        control = []
        i = 1
        moves_ = [(ff+i, rr+i), (ff-i, rr+i), (ff+i, rr-i), (ff-i, rr-i), (ff+i, rr), (ff-i, rr), (ff, rr+i), (ff, rr-i)] # define the possible moves for a castle
        for j, k in enumerate(moves_): 
            if k[0] in rank and k[1] in rank: # check the moves are on the board
                position = (file_dict_inv[k[0]], k[1])
                control.append(position)

                if board_state[position]["piece"].color == current_player:
                    pass
                else:
                    possible_moves.append(position) 
                    
        return(possible_moves, control)

class Queen(Piece):
    def __init__(self, color=0, value=9., position=("e",1)):
        Piece.__init__(self, color, value, position)
        self.label = "Q"
    
    def get_possible_moves(self, board_state, current_player):
        ff = file_dict[self.position[0]]
        rr = self.position[1]
        possible_moves = []
        control = []
        i = 1
        done_flags = [False]*8
        while i < 8: # circle outwards one move at a time, incremnting i
            moves_ = [(ff+i, rr+i), (ff-i, rr+i), (ff+i, rr-i), (ff-i, rr-i), (ff+i, rr), (ff-i, rr), (ff, rr+i), (ff, rr-i)] # define the possible moves for a castle
            for j, k in enumerate(moves_): 
                if k[0] in rank and k[1] in rank and done_flags[j] == False: # check the moves are on the board
                    position = (file_dict_inv[k[0]], k[1])
                    control.append(position)
                    if board_state[position]["piece"].color == None: # check if the moves end on a free square
                        possible_moves.append(position)
                    elif board_state[position]["piece"].color == current_player: # if the move hits my own piece, stop going that way
                        done_flags[j] = True
                    else: # if the move hits an enemy piece, stop going that way but include the enemy square.
                        possible_moves.append(position) # 
                        done_flags[j] = True
            i += 1
        return(possible_moves, control)

class Pawn(Piece):
    def __init__(self, color = 0, value = 1, position = ("b",2)):
        Piece.__init__(self, color, value, position)
        self.label = "P"
        self.moves_made = 0
    
    def get_possible_moves(self, board_state, current_player, en_passant = False):
        enemy_player = abs(1-current_player)
        ff = file_dict[self.position[0]]
        rr = self.position[1]
        possible_moves = []
        control = []
        # Set direction of pawn travel
        if current_player == 0:
            s = 1
        elif current_player == 1: # change direction of the pawns if black
            s = -1
        # Allow pawn to jump forward 2 if hasn't moved
        attack_moves = [(ff+1, rr+1*s), (ff-1, rr+1*s)]
        moves = [(ff, rr+1*s)]
        if self.n_moves == 0:
            moves.append((ff, rr+2*s))
        # somewhere add in an en passant rule
        
        for position in attack_moves:
            if position[0] in rank and position[1] in rank:
                position = (file_dict_inv[position[0]], position[1])
                control.append(position)
                if board_state[position]["piece"].color == enemy_player: # only allow attack if piece is an enemy
                    possible_moves.append(position)
        
        done_flag = False
        for position in moves:
            if position[0] in rank and position[1] in rank:
                position = (file_dict_inv[position[0]], position[1])
                if board_state[position]["piece"].label == "O" and done_flag == False: 
                    possible_moves.append(position)
                else:
                    done_flag = True
            
        return(possible_moves, control)
        
class Bishop(Piece):
    def __init__(self, color = 0, value = 3, position = ("b",2)):
        Piece.__init__(self, color, value, position)
        self.label = "B"
    
    def get_possible_moves(self, board_state, current_player):
        ff = file_dict[self.position[0]]
        rr = self.position[1]
        possible_moves = []
        control = []
        i = 1
        done_flags = [False]*4
        while i < 8: # circle outwards one move at a time, incremnting i
            moves_ = [(ff+i, rr+i), (ff-i, rr+i), (ff+i, rr-i), (ff-i, rr-i)] # define the possible moves for a castle
            for j, k in enumerate(moves_): 
                if k[0] in rank and k[1] in rank and done_flags[j] == False: # check the moves are on the board
                    position = (file_dict_inv[k[0]], k[1])
                    control.append(position)

                    if board_state[position]["piece"].color == None: # check if the moves end on a free square
                        possible_moves.append(position)
                    elif board_state[position]["piece"].color == current_player: # if the move hits my own piece, stop going that way
                        done_flags[j] = True
                    else: # if the move hits an enemy piece, stop going that way but include the enemy square.
                        possible_moves.append(position) # 
                        done_flags[j] = True
            i += 1
        return(possible_moves, control)

class Knight(Piece):
    def __init__(self, color = 0, value = 3, position = ("b",2)):
        Piece.__init__(self, color, value, position)
        self.label = "N"

    def get_possible_moves(self, board_state, current_player):
        ff = file_dict[self.position[0]]
        rr = self.position[1]
        possible_moves = []
        control = []
        moves_ = [(ff+1, rr+2), (ff+2, rr+1), (ff-2, rr-1), (ff-1, rr-2), (ff+1, rr-2), (ff-2, rr+1), (ff+2, rr-1), (ff-1, rr+2)] # define the possible moves for a castle

        for j, k in enumerate(moves_): 
            if k[0] in rank and k[1] in rank: 
                position = (file_dict_inv[k[0]], k[1])
                control.append(position)
                if board_state[position]["piece"].color == current_player: 
                    pass
                else:
                    possible_moves.append(position)
                
        return(possible_moves, control)

class Rook(Piece):
    def __init__(self, color = 0, value = 5, position = ("b",2)):
        Piece.__init__(self, color, value, position)
        self.label = "R"

    def get_possible_moves(self, board_state, current_player):
        ff = file_dict[self.position[0]]
        rr = self.position[1]
        possible_moves = []
        control = []
        i = 1
        done_flags = [False]*4
        while i < 8: # circle outwards one move at a time, incremnting i
            moves_ = [(ff+i, rr), (ff-i, rr), (ff, rr+i), (ff, rr-i)] # define the possible moves for a castle
            for j, k in enumerate(moves_): 
                if k[0] in rank and k[1] in rank and done_flags[j] == False: # check the moves are on the board
                    position = (file_dict_inv[k[0]], k[1])
                    control.append(position)
                    if board_state[position]["piece"].color == None: # check if the moves end on a free square
                        possible_moves.append(position)
                    elif board_state[position]["piece"].color == current_player: # if the move hits my own piece, stop going that way
                        done_flags[j] = True
                    else: # if the move hits an enemy piece, stop going that way but include the enemy square.
                        possible_moves.append(position) # 
                        done_flags[j] = True
            i += 1
        return(possible_moves, control)

    
# = King()

#print(K.get_possible_moves))
cb = ChessBoard()
cb.print_board()
cb.perspective = 1
cb.print_board_control()



#cb.board
#cb.update_board(("e", 2), ("e", 4))
#cb.update_board(("e", 7), ("e", 5))
#cb.update_board(("g", 1), ("f", 3))
#cb.update_board(("b", 8), ("c", 6))
#cb.update_board(("b", 7), ("b", 3))

#cb.update_board(("d",1), ("d",4))
#cb.update_board(("e",8), ("e",5))

#m = (cb.board[("d",4)]["piece"].get_possible_moves(cb.board, 0)[1])
#print(m)
#print(len(m))
#cb.print_board()
#cb.print_board_control()



cb.play_game(25, perspective = 0, wait = 0.5)

