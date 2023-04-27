"""
Vincent Brooks
https://github.com/rvbrooks

This script brings together the deep Q learning and the noughts & crosses environment.
This allows the agent to learn noughts & crosses.

TODO: play 2 agents trained on random moves against each other
TODO: train an agent against trained agent (duelling agents?)
TODO: implement pickling and loading of agents.
"""
import copy
import os
import sys
import random
import numpy as np
import matplotlib.pyplot as plt

os.environ['KMP_DUPLICATE_LIB_OK'] = 'True'  # necessary to install in import error with matplotlib and pytorch

pwd = os.path.dirname(__file__)
sys.path.append(pwd + r"\\src")
sys.path.append(pwd + r"\\in_development")

from noughts_and_crosses import Board
from DQN import Agent


class ModelTrainer:
    """Wrap model training in a class so that I can add more flexible functionality."""

    def __init__(self, agent, environment):
        self.agent = agent
        self.agent2 = copy.deepcopy(agent)
        self.b = environment
        self.score = {"X": np.array([]), "O": np.array([]), "draw": np.array([])}
        # self.X_wins, self.O_wins, self.draws = np.array([]), np.array([]), np.array([])

    def take_random_action(self, observation):
        """
        Take random actions (this is what it's being trained against)
        """
        allowed_actions = np.where(observation == 0.)[0]
        if len(allowed_actions) > 0:
            action = action_dict[random.choice(allowed_actions)]
            self.b.take_turn(action)
            observation = self.b.get_board_state()
            return (observation)

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
            last_move = (observation, action, reward, observation_, b.game_end)
            return (observation_, last_move)
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
            return (observation_)
        else:
            # There are no free places to place on the board (draw)
            self.b.take_turn((0, 0))

    def take_trained_action2(self, observation):
        """Once trained, can run the trained model with the optimal policy.
            - agent.learn() not called
            - choose_action replaced with choose_greedy_action

        """
        allowed_actions = np.where(observation == 0.)[0]
        if len(allowed_actions) > 0:
            action = self.agent2.choose_greedy_action(observation, allowed_actions)
            self.b.take_turn(action_dict[action])
            observation_ = self.b.get_board_state()
            return (observation_)
        else:
            # There are no free places to place on the board (draw)
            self.b.take_turn((0, 0))

    def train_agent(self, n_games=1, learner_player=0):
        """In order to work in punishment for losing, the moves must be played in pairs
           (so that if learner's last move led to opponent victory, gets punished).
           Agent trained against random opponenent
        """
        enemy_player = abs(1 - learner_player)
        for game in range(n_games):

            if game % int(n_games / 10) == 0:
                print(game)

            start_player = game % 2
            self.b.initialize_board(start_player)
            observation = self.b.get_board_state()

            # if learner isn't going first, make a random enemy move.
            if self.b.current_player != learner_player:
                allowed_actions = np.where(observation == 0.)[0]
                action_init = action_dict[random.choice(allowed_actions)]
                self.b.take_turn(action_init)
                observation = self.b.get_board_state()

            while not self.b.game_end:
                # if active player:
                observation0 = observation.copy()
                allowed_actions = np.where(observation0 == 0.)[0]
                if len(allowed_actions) > 0:
                    if len(allowed_actions) == self.b.board_dim ** 2:
                        action = random.choice(allowed_actions)

                    else:
                        action = self.agent.choose_action(observation0, allowed_actions)
                    self.b.take_turn(action_dict[action])
                    observation_ = self.b.get_board_state()
                    end = self.b.game_end
                else:
                    self.b.take_turn((0, 0))

                # if random player
                allowed_actions = np.where(observation_ == 0.)[0]
                if len(allowed_actions) > 0:
                    action1 = action_dict[random.choice(allowed_actions)]
                    self.b.take_turn(action1)
                    observation = self.b.get_board_state()
                else:
                    self.b.take_turn((0, 0))

                if self.b.game_end:
                    # If learner wins:
                    if self.b.win_log[Board.PLAYER_DICT[learner_player]] == 1:
                        reward = +0.2
                    # if opponent wins:
                    elif self.b.win_log[Board.PLAYER_DICT[enemy_player]] == 1:
                        reward = -0.6
                    # else draw:
                    else:
                        reward = +0.2

                self.agent.update_replay_memory(observation0, action, reward, observation_, end)
                self.agent.learn()

            for i in ["X", "O", "draw"]:
                self.score[i] = np.append(self.score[i], self.b.win_log[i])

    def train_2agents(self, n_games=1, learner_player=0):
        """Train 2 agents against each other.
            Each starts untrained and plays the other. For a given game, one player is the learner,
            and the other plays exclusively greedy actions (best policy) against them.

            The player character can be set by specifying the rewards.
        """
        agents = {1: self.agent, 0: self.agent2}
        for game in range(n_games):

            if game % int(n_games / 10) == 0:
                print(game)

            start_player = random.choice([0, 1])     # randomly choose start player
            learner_player = random.choice([0, 1])   # randomly choose learner player
            enemy_player = abs(1 - learner_player)   # set enemy player
            self.b.initialize_board(start_player)
            observation = self.b.get_board_state()

            # make a move is start player isn't learner player.
            # this is to correctly initialise the learning pair cycle.
            if self.b.current_player != learner_player:
                allowed_actions = np.where(observation == 0.)[0]
                action_init = action_dict[random.choice(allowed_actions)]
                self.b.take_turn(action_init)
                observation = self.b.get_board_state()

            # learning pair cycle: [move i: learner, mover i+1: enemy]
            while not self.b.game_end:
                # if learner player:
                observation0 = observation.copy()
                allowed_actions = np.where(observation0 == 0.)[0]
                if len(allowed_actions) > 0:
                    if len(allowed_actions) == self.b.board_dim ** 2:
                        action = random.choice(allowed_actions)
                    else:
                        action = agents[learner_player].choose_action(observation0, allowed_actions)

                    self.b.take_turn(action_dict[action])
                    observation_ = self.b.get_board_state()
                    end = self.b.game_end
                else:
                    self.b.take_turn((0, 0))

                # if random player
                allowed_actions = np.where(observation_ == 0.)[0]
                if len(allowed_actions) > 0:
                    action1 = agents[enemy_player].choose_greedy_action(observation_, allowed_actions)
                    self.b.take_turn(action_dict[action1])
                    observation = self.b.get_board_state()
                else:
                    self.b.take_turn((0, 0))

                reward_dict = {"pass": {0: 0, 1: 0},
                               "win":  {0: 1, 1: 1},
                               "lose": {0: -1, 1: -1},
                               "draw": {0: 0, 1: 0}}

                reward = reward_dict["pass"][learner_player]
                if self.b.game_end:
                    # If learner wins:
                    if self.b.win_log[Board.PLAYER_DICT[learner_player]] == 1:
                        reward = reward_dict["win"][learner_player]
                    # if opponent wins:
                    elif self.b.win_log[Board.PLAYER_DICT[enemy_player]] == 1:
                        reward = reward_dict["lose"][learner_player]
                    # else draw:
                    else:
                        reward = reward_dict["draw"][learner_player]

                agents[learner_player].update_replay_memory(observation0, action, reward, observation_, end)
                agents[learner_player].learn()

            for i in ["X", "O", "draw"]:
                self.score[i] = np.append(self.score[i], self.b.win_log[i])

    def test_policy(self, n_games, vs="random", start_player=0., print_matches=False):
        """Calculate the winrate of the trained policy against an opponent."""
        test_score = {"X": np.array([]), "O": np.array([]), "draw": np.array([])}
        if vs == "random":
            policy = self.take_random_action
            s = 1
        elif vs == "trained":
            policy = self.take_trained_action
            s = -1.
        elif vs == "learner2":
            policy = self.take_trained_action2
            s = 1

        for game in range(n_games):
            self.b.initialize_board(start_player)
            observation = self.b.get_board_state()
            observation = self.take_random_action(observation)
            while not self.b.game_end:

                if self.b.current_player == 0:

                    observation = policy(observation * s)

                elif self.b.current_player == 1:
                    # observation = self.take_random_action(observation)
                    observation = self.take_trained_action(observation)
                if print_matches == True:
                    b.print_board()
            for i in ["X", "O", "draw"]:
                test_score[i] = np.append(test_score[i], self.b.win_log[i])

        norm = np.sum(test_score["X"] + test_score["O"] + test_score["draw"])
        X_wr = np.sum(test_score["X"]) / norm
        O_wr = np.sum(test_score["O"]) / norm
        dr = np.sum(test_score["draw"]) / norm
        print("X trained, opponent : ", vs)
        print("start_player: ", Board.PLAYER_DICT[start_player])
        print("X win rate: ", X_wr)
        print("O win rate: ", O_wr)
        print("draw_rate", dr)
        print("")

    def plot_learning(self, save_plot=False):
        "Plot training results / test results"

        n = list(range(len(self.score["X"])))
        norm = np.cumsum(self.score["X"] + self.score["O"] + self.score["draw"])
        with plt.style.context("rose_pine.mplstyle"):
            plt.plot(n, np.cumsum(self.score["X"]) / norm, marker='o', label="X win")
            plt.plot(n, np.cumsum(self.score["O"]) / norm, marker='o', label="O win")
            plt.plot(n, np.cumsum(self.score["draw"]) / norm, marker='o', label="draws")

            plt.xlabel("n games")
            plt.ylabel("result occurrence")
            plt.legend()
            save_dir = pwd + r"\\plots\\noughts_crosses_results\\"

            plt.title("X is deep Q learner, O is random.")

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
    n_games = 3000
    # random.seed(2)

    b = Board(board_dim=3)

    action_dict = {i: j for i, j in enumerate(b.board)}
    input_space = [len(action_dict)]
    layer_info = [input_space, 30, len(action_dict)]

    agent = Agent(gamma=0.2,
                  alpha=0.001,
                  batch_size=100,
                  layer_dims=layer_info,
                  init_sample_size=100,
                  targ_freq=30,
                  eps_end=0.01,
                  eps_dec=1.05 / n_games
                  )

    M = ModelTrainer(agent, b)
    # M.train_agent(n_games, learner_player=1)
    M.train_2agents(n_games, learner_player=1)

    M.plot_learning(save_plot=False)
    M.test_policy(1000, vs="random", start_player=0)
    M.test_policy(1000, vs="random", start_player=1)
    M.test_policy(1000, vs="learner2", start_player=0)
    M.test_policy(1000, vs="learner2", start_player=1)

# M.test_policy(1000, vs = "trained", start_player=0)
# M.test_policy(1000, vs = "trained", start_player=1)
# M.test_policy(1000, vs = "trained", start_player=0)


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
