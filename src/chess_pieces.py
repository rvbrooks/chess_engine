"""
Define the pieces used in the chess game.
The chess pieces inherit from a parent Piece class.

TODO:
- Implement non-vanilla pieces e.g. Chancellor & Elephant

"""


file = ["a", "b", "c", "d", "e", "f", "g", "h"]
rank = [1, 2, 3, 4, 5, 6, 7, 8]
file_dict = {file[i]: rank[i] for i in range(len(rank))}
file_dict_inv = {rank[i]: file[i] for i in range(len(rank))}
castle_rank = {0: 1, 1: 8}  # rank each side castles on.


class Piece:
    def __init__(self, color=0, value=0, position=(0, 0)):
        self.value = value
        self.position = position
        self.color = color
        self.n_moves = 0
        self.label = "O"

    def __repr__(self):
        return (self.label)

    def get_label(self):
        return (self.label)

    def get_current_position(self):
        return (self.position)


    def get_possible_moves(self, board_state, current_player):
        """This is the possible moves that could be made given the type of piece
           but not yet accounting for if the space is occupied or not.  """

        possible_moves = []
        control = []

        return (possible_moves, control)


class King(Piece):
    def __init__(self, color=0, value=1000000, position=("d", 1)):
        Piece.__init__(self, color, value, position)
        self.in_check = False
        self.label = "K"

    def get_possible_moves(self, board_state, current_player):
        ff = file_dict[self.position[0]]
        rr = self.position[1]
        possible_moves = []
        control = []
        i = 1
        moves_ = [(ff + i, rr + i), (ff - i, rr + i), (ff + i, rr - i), (ff - i, rr - i), (ff + i, rr), (ff - i, rr),
                  (ff, rr + i), (ff, rr - i)]  # define the possible moves for a castle
        for j, k in enumerate(moves_):
            if k[0] in rank and k[1] in rank:  # check the moves are on the board
                position = (file_dict_inv[k[0]], k[1])
                control.append(position)

                if board_state[position]["piece"].color == current_player:
                    pass
                else:
                    possible_moves.append(position)

        return (possible_moves, control)


class Queen(Piece):
    def __init__(self, color=0, value=9., position=("e", 1)):
        Piece.__init__(self, color, value, position)
        self.label = "Q"

    def get_possible_moves(self, board_state, current_player):
        ff = file_dict[self.position[0]]
        rr = self.position[1]
        possible_moves = []
        control = []
        i = 1
        done_flags = [False] * 8
        while i < 8:  # circle outwards one move at a time, incremnting i
            moves_ = [(ff + i, rr + i), (ff - i, rr + i), (ff + i, rr - i), (ff - i, rr - i), (ff + i, rr),
                      (ff - i, rr), (ff, rr + i), (ff, rr - i)]  # define the possible moves for a castle
            for j, k in enumerate(moves_):
                if k[0] in rank and k[1] in rank and done_flags[j] == False:  # check the moves are on the board
                    position = (file_dict_inv[k[0]], k[1])
                    control.append(position)
                    if board_state[position]["piece"].color == None:  # check if the moves end on a free square
                        possible_moves.append(position)
                    elif board_state[position][
                        "piece"].color == current_player:  # if the move hits my own piece, stop going that way
                        done_flags[j] = True
                    else:  # if the move hits an enemy piece, stop going that way but include the enemy square.
                        possible_moves.append(position)  #
                        done_flags[j] = True
            i += 1
        return (possible_moves, control)


class Pawn(Piece):
    def __init__(self, color=0, value=1, position=("b", 2)):
        Piece.__init__(self, color, value, position)
        self.label = "P"
        self.moves_made = 0

    def get_possible_moves(self, board_state, current_player, en_passant=False):
        enemy_player = abs(1 - current_player)
        ff = file_dict[self.position[0]]
        rr = self.position[1]
        possible_moves = []
        control = []
        # Set direction of pawn travel
        if current_player == 0:
            s = 1
        elif current_player == 1:  # change direction of the pawns if black
            s = -1
        else:
            s = 0
            print("Current player specified incorrectly.")
        # Allow pawn to jump forward 2 if hasn't moved
        attack_moves = [(ff + 1, rr + 1 * s), (ff - 1, rr + 1 * s)]
        moves = [(ff, rr + 1 * s)]
        if self.n_moves == 0:
            moves.append((ff, rr + 2 * s))

        for position in attack_moves:
            if position[0] in rank and position[1] in rank:
                position = (file_dict_inv[position[0]], position[1])
                control.append(position)
                if board_state[position]["piece"].color == enemy_player:  # only allow attack if piece is an enemy
                    # if not final rank, don't promote
                    if position[1] != castle_rank[enemy_player]:
                        possible_moves.append(position)
                    else: # if moving onto final rank, PROMOTE!
                        promotions = ["Q", "R", "B", "N"]
                        for promotion in promotions:
                            position = (position[0], position[1], promotion)
                            possible_moves.append(position)

        done_flag = False
        for position in moves:
            if position[0] in rank and position[1] in rank:
                position = (file_dict_inv[position[0]], position[1])
                if board_state[position]["piece"].label == "O" and done_flag == False:
                    # if not final rank, don't promote
                    if position[1] != castle_rank[enemy_player]:
                        possible_moves.append(position)
                    else:  # if moving onto final rank, PROMOTE!
                        promotions = ["Q", "R", "B", "N"]
                        for promotion in promotions:
                            position = (position[0], position[1], promotion)
                            possible_moves.append(position)
                else:
                    done_flag = True

        return (possible_moves, control)


class Bishop(Piece):
    def __init__(self, color=0, value=3, position=("b", 2)):
        Piece.__init__(self, color, value, position)
        self.label = "B"

    def get_possible_moves(self, board_state, current_player):
        ff = file_dict[self.position[0]]
        rr = self.position[1]
        possible_moves = []
        control = []
        i = 1
        done_flags = [False] * 4
        while i < 8:  # circle outwards one move at a time, incremnting i
            moves_ = [(ff + i, rr + i), (ff - i, rr + i), (ff + i, rr - i),
                      (ff - i, rr - i)]  # define the possible moves for a castle
            for j, k in enumerate(moves_):
                if k[0] in rank and k[1] in rank and done_flags[j] == False:  # check the moves are on the board
                    position = (file_dict_inv[k[0]], k[1])
                    control.append(position)

                    if board_state[position]["piece"].color == None:  # check if the moves end on a free square
                        possible_moves.append(position)
                    elif board_state[position][
                        "piece"].color == current_player:  # if the move hits my own piece, stop going that way
                        done_flags[j] = True
                    else:  # if the move hits an enemy piece, stop going that way but include the enemy square.
                        possible_moves.append(position)  #
                        done_flags[j] = True
            i += 1
        return (possible_moves, control)


class Knight(Piece):
    def __init__(self, color=0, value=3, position=("b", 2)):
        Piece.__init__(self, color, value, position)
        self.label = "N"

    def get_possible_moves(self, board_state, current_player):
        ff = file_dict[self.position[0]]
        rr = self.position[1]
        possible_moves = []
        control = []
        moves_ = [(ff + 1, rr + 2), (ff + 2, rr + 1), (ff - 2, rr - 1), (ff - 1, rr - 2), (ff + 1, rr - 2),
                  (ff - 2, rr + 1), (ff + 2, rr - 1), (ff - 1, rr + 2)]  # define the possible moves for a castle

        for j, k in enumerate(moves_):
            if k[0] in rank and k[1] in rank:
                position = (file_dict_inv[k[0]], k[1])
                control.append(position)
                if board_state[position]["piece"].color == current_player:
                    pass
                else:
                    possible_moves.append(position)

        return (possible_moves, control)


class Rook(Piece):
    def __init__(self, color=0, value=5, position=("b", 2)):
        Piece.__init__(self, color, value, position)
        self.label = "R"

    def get_possible_moves(self, board_state, current_player):
        ff = file_dict[self.position[0]]
        rr = self.position[1]
        possible_moves = []
        control = []
        i = 1
        done_flags = [False] * 4
        while i < 8:  # circle outwards one move at a time, incremnting i
            moves_ = [(ff + i, rr), (ff - i, rr), (ff, rr + i), (ff, rr - i)]  # define the possible moves for a castle
            for j, k in enumerate(moves_):
                if k[0] in rank and k[1] in rank and done_flags[j] == False:  # check the moves are on the board
                    position = (file_dict_inv[k[0]], k[1])
                    control.append(position)
                    if board_state[position]["piece"].color == None:  # check if the moves end on a free square
                        possible_moves.append(position)
                    elif board_state[position]["piece"].color == current_player:  # if the move hits my own piece, stop going that way
                        done_flags[j] = True
                    else:  # if the move hits an enemy piece, stop going that way but include the enemy square.
                        possible_moves.append(position)  #
                        done_flags[j] = True
            i += 1
        return (possible_moves, control)

if __name__ == "__main__":
    piece = Pawn()
    print(piece)