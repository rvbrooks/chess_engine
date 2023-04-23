import os
import sys
import random
import numpy as np
import matplotlib.pyplot as plt

os.environ['KMP_DUPLICATE_LIB_OK']='True' # necessary to install in import error with matplotlib and pytorch

pwd = os.path.dirname(__file__)
sys.path.append(pwd+r"\\src")
sys.path.append(pwd+r"\\in_development")


from chess_environment import ChessBoard
from noughts_and_crosses import Board
from DQN import Agent

if __name__ == "__main__":
    b = Board(board_dim=3, start_player = 0)
    random.seed()

    len_action_space = len(b.board) # action space is the number of board squares
    action_dict = {i : j for i, j in enumerate(b.board)}
    n_games = 1000
    input_space = [len(action_dict)]

    ld = [input_space, 15, 15, len(action_dict)]
    agent = Agent(gamma=0.95,
                  epsilon=1.0,
                  alpha=0.001,
                  batch_size=90,
                  layer_dims=ld,
                  init_sample_size=90,
                  targ_freq=90,
                  eps_end=0.01,
                  eps_dec=0.0005)

    # 3. Set up cycle of take observation of board state
    X_wins = np.array([])
    O_wins = np.array([])
    draws = np.array([])
    smart = True
    for game in range(n_games):
        b.initialize_board()
        observation = b.get_board_state()

        if game % int(n_games/10) == 0:
            print(game)

        while not b.game_end:
            allowed_actions = np.where(observation == 0.)[0]
            # random moves of opposition
            if b.current_player == 0:
                if len(allowed_actions) > 0:
                    action = action_dict[random.choice(allowed_actions)]
                    b.take_turn(action)
                else:
                    # There are no free places to place on the board (draw)
                    b.take_turn((0,0))

            # learning moves of the player
            elif b.current_player == 1:
                if smart == False:
                    if len(allowed_actions) > 0:
                        action = action_dict[random.choice(allowed_actions)]
                        b.take_turn(action)
                    else:
                        # There are no free places to place on the board (draw)
                        b.take_turn((0,0))
                else:
                    if len(allowed_actions) > 0:
                        action = agent.choose_action(observation, allowed_actions)
                        b.take_turn(action_dict[action])
                        observation_ = b.get_board_state()
                        agent.update_replay_memory(observation, action, b.game_reward, observation_, b.game_end)
                        agent.learn()
                        observation = observation_
                    else:
                        # There are no free places to place on the board (draw)
                        b.take_turn((0,0))

        #b.print_board()
        X_wins = np.append(X_wins, b.win_log["X"])
        O_wins = np.append(O_wins, b.win_log["O"])
        draws = np.append(draws, b.win_log["draw"])

    n = list(range(n_games))
    norm = X_wins + O_wins + draws
    with plt.style.context("rose_pine.mplstyle"):
        plt.plot(n, X_wins/norm, marker = 'o', label = "X win")
        plt.plot(n, O_wins/norm, marker = 'o', label = "O win")
        plt.plot(n, draws/norm, marker = 'o',  label = "draws")

        plt.xlabel("n games")
        plt.ylabel("result occurrence")
        plt.legend()
        plt.show(block=True)

    print("win_log")
    print(b.win_log)




