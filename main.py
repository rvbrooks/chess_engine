"""
Vincent Brooks
https://github.com/rvbrooks

This script brings together the deep Q learning and the noughts & crosses environment.
This allows the agent to learn noughts & crosses.

TODO: play 2 agents trained on random moves against each other
TODO: train an agent against trained agent (duelling agents?)
TODO: implement pickling and loading of agents.
"""

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


class ModelTrainer:
    """Wrap model training in a class so that I can add more flexible functionality."""
    def __init__(self, agent, environment):
        self.agent = agent
        self.b = environment
        self.score = {"X":np.array([]), "O":np.array([]), "draw":np.array([])}
        #self.X_wins, self.O_wins, self.draws = np.array([]), np.array([]), np.array([])

    def take_random_action(self, observation):
        """
        Take random actions (this is what it's being trained against)
        """
        allowed_actions = np.where(observation == 0.)[0]
        if len(allowed_actions) > 0:
            action = action_dict[random.choice(allowed_actions)]
            self.b.take_turn(action)
            observation = self.b.get_board_state()
            return(observation)

        else:
            # There are no free places to place on the board (draw)
            self.b.take_turn((0, 0))

    def take_learner_action(self, observation):
        """
        For a learning deep Q model, take an action & learn while updating replay memory.

        """
        allowed_actions = np.where(observation == 0.)[0]
        if len(allowed_actions) > 0:
            action = self.agent.choose_action(observation, allowed_actions)
            self.b.take_turn(action_dict[action])
            observation_ = self.b.get_board_state()
            reward = self.b.game_reward
            self.agent.update_replay_memory(observation, action, reward, observation_, b.game_end)
            self.agent.learn()
            return(observation_)
        else:
            # There are no free places to place on the board (draw)
            self.b.take_turn((0, 0))

    def take_trained_action(self, observation):
        """Once trained, can run the trained model with the optimal policy.
            - agent.learn() not called
            - choose_action replaced with choose_greedy_action

        """
        allowed_actions = np.where(observation == 0.)[0]
        if len(allowed_actions) > 0:
            action = self.agent.choose_greedy_action(observation, allowed_actions)
            self.b.take_turn(action_dict[action])
            observation_ = self.b.get_board_state()
            reward = self.b.game_reward
            self.agent.update_replay_memory(observation, action, reward, observation_, b.game_end)
            return(observation_)
        else:
            # There are no free places to place on the board (draw)
            self.b.take_turn((0, 0))

    def train_agent(self, n_games = 1):
        """This is where the DQN would be trained
        TODO: Would be nice to be able to go back and train the agent further at a later time.
        """
        for game in range(n_games):
            self.b.initialize_board()
            observation = self.b.get_board_state()

            if game % int(n_games / 10) == 0:
                print(game)

            while not self.b.game_end:

                if self.b.current_player == 0:
                    observation = self.take_random_action(observation)

                elif self.b.current_player == 1:
                    observation = self.take_learner_action(observation)

            for i in ["X", "O", "draw"]:
                self.score[i] = np.append(self.score[i], self.b.win_log[i])

        #wr = np.sum(self.score["X"][-100:]) / np.sum(self.score["X"][-100:] + self.score["O"][-100:] + self.score["draw"][-100:])
        #print("trained winrate: ", wr)


    def test_policy(self, n_games):
        """Calculate the winrate of the trained policy against an opponent."""
        test_score = {"X":np.array([]), "O":np.array([]), "draw":np.array([])}
        for game in range(n_games):
            self.b.initialize_board()
            observation = self.b.get_board_state()

            while not self.b.game_end:

                if self.b.current_player == 0:
                    observation = self.take_random_action(observation)
                    #observation = self.take_trained_action(observation)

                elif self.b.current_player == 1:
                    observation = self.take_trained_action(observation)

            for i in ["X", "O", "draw"]:
                test_score[i] = np.append(test_score[i], self.b.win_log[i])

        norm = np.sum(test_score["X"] + test_score["O"] + test_score["draw"])
        X_wr = np.sum(test_score["X"]) / norm
        O_wr = np.sum(test_score["O"]) / norm
        dr = np.sum(test_score["draw"]) / norm

        print("X win rate: ", X_wr)
        print("O win rate: ", O_wr)
        print("draw_rate", dr)

    def plot_results(self, save_plot=False):
        "Plot training results / test results"

        n = list(range(len(self.score["X"])))
        norm = np.cumsum(self.score["X"]+self.score["O"]+self.score["draw"])
        with plt.style.context("rose_pine.mplstyle"):
            plt.plot(n, np.cumsum(self.score["X"]) / norm, marker='o', label="X win")
            plt.plot(n, np.cumsum(self.score["O"]) / norm, marker='o', label="O win")
            plt.plot(n, np.cumsum(self.score["draw"]) / norm, marker='o', label="draws")

            plt.xlabel("n games")
            plt.ylabel("result occurrence")
            plt.legend()
            save_dir = pwd + r"\\plots\\noughts_crosses_results\\"

            plt.title("Start player = {}; X is deep Q learner, O is random.".format(Board.PLAYER_DICT[start_player]))

            if save_plot:
                filename = "start_player=" + Board.PLAYER_DICT[start_player] + ".png"
                plt.savefig(save_dir + filename)

            plt.show(block=True)

    def save_trained_agent(self):
        """Pickle the agent to load at some later point."""
        pass

    def load_trained_agent(self):
        """Load a pickled agent to run it"""
        pass

if __name__ == "__main__":

    start_player = 1
    n_games = 3000
    random.seed(2)

    b = Board(board_dim=3, start_player = start_player)

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

    M = ModelTrainer(agent, b)
    M.train_agent(n_games)
    M.plot_results(save_plot=False)
    M.test_policy(1000)



#
# # Should have 0% loss rate if trained.
#
# # what could be going wrong that it doesn't train well
# # A. Bug in the code
# #   - check what the observation being fed into NN is.
# # B. Bad hyperparameters / rewards
# #   - Understand better time difference & gamma
# # C. Try modifying NN:
# #   - penalise forbidden choices rather than remove from selection
# #   - He initialisation
# #   - Huber loss



