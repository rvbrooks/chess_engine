import torch as T
import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim
import numpy as np
import copy

# https://towardsdatascience.com/reinforcement-learning-explained-visually-part-5-deep-q-networks-step-by-step-5a5317197f4b#:~:text=The%20Target%20network%20predicts%20Q,of%20all%20those%20Q%2Dvalues.

import random
#random.seed(1)

class DeepQNetwork(nn.Module):
    def __init__(self, alpha, dims=None):
        super().__init__()
        self.n_layers = len(dims)

        # https://stackoverflow.com/questions/54678896/pytorch-valueerror-optimizer-got-an-empty-parameter-list
        # supply layer dimensions as a list -> should make modification easier.
        self.layer_list = nn.ModuleList()
        for i in range(len(dims) - 1):
            if i == 0:
                self.layer_list.append(nn.Linear(*dims[i], dims[i+1]))
            else:
                self.layer_list.append(nn.Linear(dims[i], dims[i+1]))

        self.optimizer = optim.Adam(self.parameters(), lr = alpha)
        
        self.loss = nn.MSELoss()
        
        self.device = T.device("cuda:0" if T.cuda.is_available() else "cpu")
        
        self.to(self.device)
        
    def forward(self, state):
        x = state
        for layer in range(len(self.layer_list)-1):
            x = F.relu(self.layer_list[layer](x))
        actions = self.layer_list[-1](x)

        return(actions)

class Agent():
    """
    The agent owns several objects:
        - A QNN
        - A Target NN
        - State memory
    """
    def __init__(self, gamma, epsilon, alpha, layer_dims, batch_size, init_sample_size = 1000,
                 max_mem_size=100000, eps_end=0.01, eps_dec=1e-5, targ_freq=100):

        # layer dimensions: list of type [input_size, l1_size, l2_size, ..., ln_size, action_size]

        self.gamma = gamma
        self.epsilon = epsilon
        self.eps_min = eps_end
        self.eps_dec = eps_dec
        self.alpha = alpha
        self.target_update_freq = targ_freq
        self.init_sample_size = init_sample_size
        
        self.action_space = [i for i in range(layer_dims[-1])]
        
        self.mem_size = max_mem_size # this is size of the memory data set (e.g. N samples)
        self.batch_size = batch_size # this is how many samples you draw from replay in a given training
        self.mem_cntr = 0

        # Instantiate the Q network.
        self.Q_eval = DeepQNetwork(self.alpha, layer_dims)

        # Instantiate the target network.
        self.Q_target = copy.deepcopy(self.Q_eval)
        
        # Replay is (state, new_state, action, reward)
        self.state_memory = np.zeros((self.mem_size, *layer_dims[0]), dtype=np.float32)
        self.new_state_memory = np.zeros((self.mem_size, *layer_dims[0]),dtype=np.float32)
        self.action_memory = np.zeros((self.mem_size),dtype=np.int32)
        self.reward_memory = np.zeros((self.mem_size),dtype=np.float32)
        self.terminal_memory = np.zeros((self.mem_size), dtype=bool)
                
    def update_replay_memory(self, state, action, reward, state_, done):
        """store current observation in replay memory
           this adds a new sample to the memory and overwrites if full.
        """
        
        index = self.mem_cntr % self.mem_size

        self.state_memory[index] = state
        self.new_state_memory[index] = state_
        self.reward_memory[index] = reward
        self.action_memory[index] = action
        self.terminal_memory[index] = done

        
        self.mem_cntr += 1
        
    def choose_action(self, observed_state, allowed_actions):

        # Q-greedy: exploit.
        if np.random.random() > self.epsilon:
            state = T.tensor([observed_state]).to(self.Q_eval.device)
            actions = self.Q_eval.forward(state) # this is a tensor of Q values

            # restrict the possible moves to those allowed by the state of the board.
            allowed_qvals = [actions[0, i].item() for i in allowed_actions]
            action = allowed_actions[np.argmax(allowed_qvals)]

        # Explore.
        else:
            action = np.random.choice(allowed_actions)
        
        return(action)

    def learn(self):

        if self.mem_cntr < self.init_sample_size:
            return

        self.Q_eval.optimizer.zero_grad()

        max_mem = min(self.mem_cntr, self.mem_size)

        # BATCH is a number of samples drawn from the replay memory.
        batch = np.random.choice(max_mem, self.batch_size, replace=False)
        # index the samples in the batch with an integer.
        batch_index = np.arange(self.batch_size, dtype=np.int32)
        
        state_batch = T.tensor(self.state_memory[batch]).to(self.Q_eval.device)
        new_state_batch = T.tensor(self.new_state_memory[batch]).to(self.Q_eval.device)

        reward_batch = T.tensor(self.reward_memory[batch]).to(self.Q_eval.device)      
        action_batch = self.action_memory[batch]                                        

        q_eval = self.Q_eval.forward(state_batch)[batch_index, action_batch]
        q_next = self.Q_target.forward(new_state_batch) 

       # q_target = (1-self.gamma)*reward_batch + self.gamma * T.min(q_next, dim=1)[0]
        q_target = reward_batch + self.gamma * T.max(q_next, dim=1)[0]

        loss = self.Q_eval.loss(q_target, q_eval).to(self.Q_eval.device) # just calculating loss func
        loss.backward() # updates the weights
        self.Q_eval.optimizer.step()
        
        if self.epsilon > self.eps_min:
            self.epsilon = self.epsilon - self.eps_dec  
        else:
            self.epsilon = self.eps_min

        if self.mem_cntr % self.target_update_freq == 0:
            self.Q_target = copy.deepcopy(self.Q_eval)


if __name__ == "__main__":

    input_space = [15]
    l1, l2 = 30, 30
    action_space = 15

    ld = [input_space, l1, l2, action_space]

    agent = Agent(gamma=0.99,
                  epsilon=1.0,
                  alpha=0.1,
                  batch_size=300,
                  layer_dims=ld,
                  init_sample_size=1000,
                  targ_freq=200,
                  eps_end=0.01,
                  eps_dec=0.00005)
    
    epsilons = []

   # agent.choose_action([1]*15, [1]*15)
    
