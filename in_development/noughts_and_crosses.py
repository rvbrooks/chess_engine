"""
Simple coding of the game Noughts & Crosses.
This will be a super simple proxy for chess to have a go coding a deep Q network for a game.
"""

import random


# DQN: agent will take action.

class Board:
    PLAYER_DICT = {0: "O", 1: "X"}

    def __init__(self, start_player=0, board_dim = 3):
        self.board_dim = board_dim
        self.board_idx = range(self.board_dim)
        self.empty_marker = "."
        self.turn = 0
        self.start_player = start_player
        self.current_player = start_player
        self.board = {}
        self.initialize_board()
        self.win_conditions = []
        self.get_victory_conditions()
        self.game_end = False

    def initialize_board(self):
        for i in self.board_idx:
            for j in self.board_idx:
                self.board[(i, j)] = self.empty_marker
        self.print_board()
        self.turn = 0
        self.current_player = self.start_player

    def play_game(self):
        while not self.game_end:
            x = random.choice(b.board_idx)
            y = random.choice(b.board_idx)
            if self.turn < self.board_dim ** 2:
                self.take_turn((x, y))
            else:
                print("Draw!")
                break

    def take_turn(self, position):
        self.current_player = self.turn % 2
        if self.board[position] == self.empty_marker:
            self.board[position] = Board.PLAYER_DICT[self.current_player]
            self.assess_board()
            self.print_board()
            self.turn += 1
        else:
            print("That square already has a piece in it! Try again.")

    def get_victory_conditions(self):
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

    def assess_board(self):
        """Check for victory against the 8 possibilities for each side"""

        for line in self.win_conditions:
            control = ""
            for position in line:
                control += self.board[position]
            if control == Board.PLAYER_DICT[self.current_player]*self.board_dim:
                print("\n {} victory!".format(Board.PLAYER_DICT[self.current_player]))
                self.game_end = True

    def get_board_state(self):
        """Get the encoded board state for the deep Q network
           Should return a dictionary of {index : -1/0/1}
        """
        indexed_states = {i : j for i, j in enumerate(self.board)}
        observed_state = {}

        for i in indexed_states:
            position = indexed_states[i]
            if self.board[position] == "O":
                observed_state[i] = -1
            elif self.board[position] == "X":
                observed_state[i] = 1
            elif self.board[position] == self.empty_marker:
                observed_state[i] = 0

        return observed_state

    def print_board(self, verbose=False):
        """Print out the board. Verbose will print the coordinates too."""
        if verbose == True:
            for i in self.board_idx:
                print(" ")
                for j in self.board_idx:
                    print((i, j), end=" ")

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
    b.take_turn((0,1))
    b.take_turn((2,2))
    b.take_turn((1,1))

    o = b.get_board_state()
    all_actions = list(range(len(o)))
    print("o", o)
    print(all_actions)
    mask = [None if o[i] != 0 else i for i in o ]
    print("mask", mask)

    allowed_actions = [i for i in all_actions if mask[i] not in [None]]
    print("aa", allowed_actions)


