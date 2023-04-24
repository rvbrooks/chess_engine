![alt text](https://github.com/rvbrooks/chess_engine/blob/main/images/chess_banner_2.png)

Deep Blue beats Gary Kasparov in 1997: the first time an artificial intelligence outperforms a human chess world champion.

Most of my life, it has been a fact that computers outperform even the best human players at chess. This has always fascinated me, especially now that the AI revolution is underway: algorithms that were once confined to games of chess are being used to solve far-reaching and meaningful problems globally.


## About my **chess_engine** project
In this ongoing project, I'm aiming to apply similar deep reinforcement learning (DRL) methods to one of the most advanced chess AI engines: [DeepMind's AlphaZero](https://arxiv.org/pdf/1712.01815.pdf).

## Roadmap

#### ✅ Define the rules of chess
  - For personal interest, I coded up the rules of chess rather than using an existing Python library.
  - *Status*: 
       - ✅ The computer can play a completely random game against itself, with support for the special move cases of castling, en-passant and pawn promotion
       - ✅ The board state and board square control can be printed out for each move in the game.
       - ☐  Most win conditions are accounted for, except for resignation / offered draw / 3-fold repition and the 50 move rule.

#### ✅ Implement deep Q learning for an easier game.
  - Going straight to deep reinforcement learning in chess is a big jump. First I will try some reinforcement learning on a simple game. Noughts & Crosses (N&C) is extremely simple and should be easy to get working.
  - *Status*:
      -  ✅ Coded up the rules of Noughts & Crosses.
      -  ✅ Implement deep reinforcement learning for N&C.
      -  ✅ Winrate for a trained policy when going first vs a randomly acting opponent is ~98%, which is best expected.
      -  ✅ Winrate for a trained policy when going second vs a randomly acting opponent is ~82%, which is best expected.
      -  ☐ Play 2 trained agents against each other -> expect 100% draw rate.
      -  ☐ Document results and process in more detail.

#### ☐ Choose a model for chess learning
##### Reinforcement Learning
 - There are many models that have been used to write chess AIs. My aim is to code a DRL model for chess, however being quite advanced it may make sense to consider other approaches firt.
 - I will build a DRL model for a simpler game like Noughts & Crosses, to better understand the deep learning approach.
 - I will train the chess model to solve reduced-complexity examples like simple endgames, as a PoC.

##### Supervised Learning
 - I expect it is possible to train a supervised model on the vast database of games that have been played. I would be interesting to compare using this approach.


## Project Structure
```
chess_engine
├── docs   
├── src 
├── test
├── tools
└── README.md
```
