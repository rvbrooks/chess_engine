import os
import sys
import random
import numpy as np
import matplotlib.pyplot as plt

os.environ['KMP_DUPLICATE_LIB_OK']='True' # necessary to install in import error with matplotlib and pytorch

pwd = os.path.dirname(__file__)
sys.path.append(pwd+r"\\src")
sys.path.append(pwd+r"\\in_development")


from noughts_and_crosses import Board
from DQN import Agent

if __name__ == "__main__":
    p = {0:"O",1:"X"}

    start_player = 1
    n_games = 1000
    save_plot = False
    random.seed(2)

    b = Board(board_dim=3, start_player = start_player)

    len_action_space = len(b.board) # action space is the number of board squares
    action_dict = {i : j for i, j in enumerate(b.board)}
    input_space = [len(action_dict)]

    ld = [input_space, 30, len(action_dict)]
    agent = Agent(gamma=0.1,
                  alpha=0.001,
                  batch_size=100,
                  layer_dims=ld,
                  init_sample_size=100,
                  targ_freq=100,
                  eps_end=0.01,
                  eps_dec=1.05/n_games
                  )

    X_wins, O_wins, draws = np.array([]), np.array([]), np.array([])
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
                    observation = b.get_board_state()

                else:
                    # There are no free places to place on the board (draw)
                    b.take_turn((0,0))

            # learning moves of the player
            elif b.current_player == 1:

                if len(allowed_actions) > 0:

                    action = agent.choose_action(observation, allowed_actions)
                    b.take_turn(action_dict[action])
                    observation_ = b.get_board_state()
                    reward = b.game_reward
                    agent.update_replay_memory(observation, action, reward, observation_, b.game_end)
                    agent.learn()
                    observation = observation_
                else:
                    # There are no free places to place on the board (draw)
                    b.take_turn((0,0))


        X_wins = np.append(X_wins, b.win_log["X"])
        O_wins = np.append(O_wins, b.win_log["O"])
        draws = np.append(draws, b.win_log["draw"])
    wr = np.sum(X_wins[-100:])/np.sum(X_wins[-100:] + O_wins[-100:] + draws[-100:])
    print("trained winrate: ", wr)

    n = list(range(n_games))
    norm = np.cumsum(X_wins + O_wins + draws)
    with plt.style.context("rose_pine.mplstyle"):

        plt.plot(n, np.cumsum(X_wins)/norm, marker = 'o', label = "X win")
        plt.plot(n, np.cumsum(O_wins)/norm, marker = 'o', label = "O win")
        plt.plot(n, np.cumsum(draws)/norm, marker = 'o',  label = "draws")

        plt.xlabel("n games")
        plt.ylabel("result occurrence")
        plt.legend()
        save_dir = pwd + r"\\plots\\noughts_crosses_results\\"

        plt.title("Start player = {}; X is deep Q learner, O is random.".format(p[start_player]))

        if save_plot == True:
            filename = "start_player=" + p[start_player] + ".png"
            plt.savefig(save_dir + filename)

        plt.show(block=True)

# Should have 0% loss rate if trained.

# what could be going wrong that it doesn't train well
# A. Bug in the code
#   - check what the observation being fed into NN is.
# B. Bad hyperparameters / rewards
#   - Understand better time difference & gamma
# C. Try modifying NN:
#   - penalise forbidden choices rather than remove from selection
#   - He initialisation
#   - Huber loss
#
# TODO: when working, separate this into its own file
#
#
#





