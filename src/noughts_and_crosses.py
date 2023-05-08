"""
Vincent Brooks
https://github.com/rvbrooks

My implementation of a game environment for Noughts & Crosses.

"""
import numpy as np
import random


# DQN: agent will take action.

class Board:
    PLAYER_DICT = {0: "O", 1: "X"}

    def __init__(self, board_dim = 3):
        self.board_dim = board_dim
        self.board_idx = range(self.board_dim)
        self.empty_marker = "."
        self.turn = 0
        self.board = {}
        self.initialize_board()
        self.win_conditions = []
        self.get_victory_conditions()
        self.game_end = False
        self.win_log = {"O":0,"X":0,"draw":0}

    def initialize_board(self, start_player=0):
        """
        (Re)-Initializes board to empty state, and environment variables to start state values.
        """
        for i in self.board_idx:
            for j in self.board_idx:
                self.board[(i, j)] = self.empty_marker

        self.turn = 0
        self.current_player = start_player

        self.game_end = False
        self.game_reward = 0
        self.win_log = {"O":0,"X":0,"draw":0}

    def play_game(self):
        """
        Test function not used for DRL.
        Plays 2 random actors against each other until game completion.
        """
        while not self.game_end:
            x = random.choice(b.board_idx)
            y = random.choice(b.board_idx)
            if self.turn < self.board_dim ** 2:
                self.take_turn((x, y))
            else:
                print("Draw!")
                self.win_log["draw"] += 1
                break

    def take_turn(self, position):
        """
        Take a turn in Noughts & Crosses (place an X or a O).
        Input:
            - position: where on the board to place the X or O.
        Output:
            - updated environment
            - updated current player
            - checks for win / draw condition.

        """
        if self.board[position] == self.empty_marker:
            self.board[position] = Board.PLAYER_DICT[self.current_player]
            self.assess_board()
            self.turn += 1
        else:
            if 0 not in self.get_board_state() and not self.game_end:
                self.game_end = True
                self.win_log["draw"] += 1
                self.game_reward = 1
        self.current_player = abs(1-self.current_player)

    def assess_board(self):
        """Check for victory against the 8 possibilities for each side"""
        for line in self.win_conditions:
            control = ""
            for position in line:
                control += self.board[position]
            if control == Board.PLAYER_DICT[self.current_player]*self.board_dim and not self.game_end:
               # print("\n {} victory!".format(Board.PLAYER_DICT[self.current_player]))
                self.game_end = True
                self.win_log[Board.PLAYER_DICT[self.current_player]] += 1

    def get_board_state(self):
        """Get the encoded board state for the deep Q network
           Should return an array of {index : -1/0/1}
           Outputs:
                - observation: a list of the observed positions of X's & O's.
        """
        indexed_states = {i : j for i, j in enumerate(self.board)}
        observed_state = []

        for i in indexed_states:
            position = indexed_states[i]
            if self.board[position] == "O":
                observed_state.append(-1.)
            elif self.board[position] == "X":
                observed_state.append(1.)
            elif self.board[position] == self.empty_marker:
                observed_state.append(0.)

        return np.array(observed_state, dtype=np.float32)

    def get_victory_conditions(self):
        """Noughts & Crosses is won when a line of X's or O's is achieved.
           This function gets the lines  of baord coordinates along which this can be achieved.
        """
        valid_lines = []

        line_diag_1 = []
        line_diag_2 = []
        for i in self.board_idx:
            line_v = []
            line_h = []

            line_diag_1.append((i, i))
            line_diag_2.append((i, self.board_dim - (i + 1)))

            for j in self.board_idx:
                line_v.append((i, j))
                line_h.append((j,i))

            valid_lines.append(line_v)
            valid_lines.append(line_h)
        valid_lines.append(line_diag_1)
        valid_lines.append(line_diag_2)
        self.win_conditions = valid_lines

    def print_board(self):
        """Print out the board state with O's and X's."""

        for i in self.board_idx:
            print(" ")
            for j in self.board_idx:
                print(self.board[(i, j)], end=" ")

        print("")


# How do I represent the states to a neural network?
# I expect that I would have 9 inputs corresponding to each square of the board.
# Then depending on what had been placed, you'd set the value to -1 or 0 or 1.
# Then passing through the network, you'd spit out an action, which would be
# "place on position X"
# Would I have 2 networks competing? How do I make them know which side they're playing?
# Can test by playing one network against a randomly choosing network.

if __name__ == "__main__":
    b = Board(board_dim = 3)
    b.play_game()

   # o = b.get_board_state()
   # print(o)
    b.print_board()


# Lessons:
# For binary states, you want them to be substantially different;
# when using X=1 and O=2 encoding, it didn't train well (65% winrate)
# when using X=1, O=-1 winrate, it had 97% winrate.
