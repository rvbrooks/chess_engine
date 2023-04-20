import os
import sys
import random
pwd = os.path.dirname(__file__)
sys.path.append(pwd+r"\\src")
sys.path.append(pwd+r"\\in_development")


from chess_environment import ChessBoard
from noughts_and_crosses import Board
from DQN import Agent

if __name__ == "__main__":
    b = Board()

    len_action_space = len(b.board) # action space is the number of board squares
    action_dict = {i : j for i, j in enumerate(b.board)}

    n_games = 5
    input_space = [len(action_dict)]

    ld = [input_space, 15, 15, len(action_dict)]
    agent = Agent(gamma=0.99,
                  epsilon=1.0,
                  alpha=0.1,
                  batch_size=300,
                  layer_dims=ld,
                  init_sample_size=1000,
                  targ_freq=200,
                  eps_end=0.01,
                  eps_dec=0.00005)

    # 3. Set up cycle of take observation of board state
    for game in range(n_games):
        b.initialize_board()
        observation = b.get_board_state()

        while not b.game_end:
            # random moves of opposition
            if b.current_player == 0:
                x = random.choice(b.board_idx)
                y = random.choice(b.board_idx)
                if b.turn < b.board_dim ** 2:
                    b.take_turn((x, y))

            # learning moves of the player
            elif b.current_player == 1:
                while True: # TODO: add in correct conditions
                    # Like for my chess engine, need to make it unable to place on a filled space.
                    # remove action from action space if no longer possible.
                    action = agent.choose_action(observation)  # based on current state of env.
                    b.take_turn(action_dict[action])
                    observation_ = b.get_board_state()

                agent.store_transition(observation, action, reward, observation_, done)
                agent.learn()
                observation = observation_
