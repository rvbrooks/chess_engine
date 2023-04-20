import torch as T
import torch.nn as nn
import torch.nn.functional as F # to use ReLu for DNN
import torch.optim as optim # for Adam optimiser
import numpy as np
import gym
import matplotlib.pyplot as plt

# https://towardsdatascience.com/reinforcement-learning-explained-visually-part-5-deep-q-networks-step-by-step-5a5317197f4b#:~:text=The%20Target%20network%20predicts%20Q,of%20all%20those%20Q%2Dvalues.



import random
random.seed(1)


class DeepQNetwork(nn.Module):
    def __init__(self, alpha, input_dims, fc1_dims, fc2_dims, n_actions):
        super().__init__()
        self.input_dims = input_dims
        self.fc1_dims = fc1_dims
        self.fc2_dims = fc2_dims
        self.n_actions = n_actions

        self.fc1 = nn.Linear(*self.input_dims, self.fc1_dims)
        self.fc2 = nn.Linear(self.fc1_dims, self.fc2_dims)
        self.fc3 = nn.Linear(self.fc2_dims, self.n_actions)

        self.optimizer = optim.Adam(self.parameters(), lr = alpha)
        
        self.loss = nn.MSELoss()
        
        self.device = T.device("cuda:0" if T.cuda.is_available() else "cpu")
        
        self.to(self.device)
        
    def forward(self, state):

        x = F.relu(self.fc1(state)) 
        x = F.relu(self.fc2(x))
        actions = self.fc3(x)

        return(actions)


    
    
class Agent():
    """
    The agent owns several objects:
        - A QNN
        - A Target NN
        - State memory
    """
    def __init__(self, gamma, epsilon, alpha, input_dims, batch_size, n_actions, init_sample_size = 1000,
                 max_mem_size=100000, eps_end=0.01, eps_dec=1e-5, target_update_freq=100):
        
        self.gamma = gamma
        self.epsilon = epsilon
        self.eps_min = eps_end
        self.eps_dec = eps_dec
        self.alpha = alpha
        self.target_update_freq = target_update_freq
        self.init_sample_size = init_sample_size
        
        self.action_space = [i for i in range(n_actions)]
        
        self.mem_size = max_mem_size # this is size of the memory data set (e.g. N samples)
        self.batch_size = batch_size # this is how many samples you draw from replay in a given training
        self.mem_cntr = 0
       
        self.Q_eval = DeepQNetwork(self.alpha, n_actions=n_actions, input_dims=input_dims, 
                                   fc1_dims=30, fc2_dims=30)
        
        self.Q_target = DeepQNetwork(self.alpha, n_actions=n_actions, input_dims=input_dims, 
                                   fc1_dims=30, fc2_dims=30)
        
        # Replay is (state, new_state, action, reward)
        self.state_memory = np.zeros((self.mem_size, *input_dims), dtype=np.float32)
        self.new_state_memory = np.zeros((self.mem_size, *input_dims),dtype=np.float32)
        self.action_memory = np.zeros((self.mem_size),dtype=np.int32)
        self.reward_memory = np.zeros((self.mem_size),dtype=np.float32)
                
    def update_replay_memory(self, state, action, reward, state_):
        """store current observation in replay memory
           this adds a new sample to the memory and overwrites if full.
        """
        
        index = self.mem_cntr % self.mem_size

        self.state_memory[index] = state
        self.new_state_memory[index] = state_
        self.reward_memory[index] = reward
        self.action_memory[index] = action
        
        self.mem_cntr += 1
        
    def choose_action(self, observed_state, AA):
        """this is jsut the epsilon greedy make choice"""

        if np.random.random() > self.epsilon:
           # print("greedy")
            state = T.tensor([observed_state]).to(self.Q_eval.device)
            actions = self.Q_eval.forward(state) # this is a tensor of Q values


            allowed_qvals = []
            for i in allowed_actions:
                allowed_qvals.append(actions[0,i].item())
            min_q_idx = np.argmin(allowed_qvals)
            action = allowed_actions[min_q_idx] # the action here is the integer which labels a codon.

        else:
           # print("explore")
            action = np.random.choice(codon_index_dict[AA])
        
        return(action)

    
    def learn(self):
       
        # this statement is saying that if the replay memory is not sufficeintly full
        # (data points < batch size), then SKIP the learning
        if self.mem_cntr < self.init_sample_size:
            # don't bother learning
            return
        
        # once sufficently full, the learning part actually does something.

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

        q_target = (1-self.gamma)*reward_batch + self.gamma * T.min(q_next, dim=1)[0]

        loss = self.Q_eval.loss(q_target, q_eval).to(self.Q_eval.device) # just calculating loss func
        loss.backward() # updates the weights
        self.Q_eval.optimizer.step()
        
        if self.epsilon > self.eps_min:
            self.epsilon = self.epsilon - self.eps_dec  
        else:
            self.epsilon = self.eps_min


        # update target network by overwriting it with the Q_eval network every k runs
        
        if self.mem_cntr % self.target_update_freq == 0:
            self.Q_target = self.Q_eval


if __name__ == "__main__":

    agent = Agent(gamma=0.99, epsilon=1.0, batch_size=300, n_actions=len(env.action_space),
                  init_sample_size = init_sample_size, target_update_freq = 200,
                  eps_end = 0.01, input_dims=[len(env.input_space)], alpha=0.1, eps_dec=epsilon_decrement)
    
    epsilons = []
    
