![alt text](https://github.com/rvbrooks/chess_engine/blob/main/images/chess_banner_2.png)

Deep Blue beats Gary Kasparov in 1997: the first time an artificial intelligence outperforms a human chess world champion.

Most of my life, it has been a fact that computers outperform even the best human players at chess. This has always fascinated me, especially now that the AI revolution is underway: algorithms that were once confined to games of chess are being used to solve far-reaching and meaningful problems globally.


## About my **chess_engine** project
In this ongoing project, I'm aiming to apply similar deep reinforcement learning (DRL) methods to one of the most advanced chess AI engines: [DeepMind's AlphaZero](https://arxiv.org/pdf/1712.01815.pdf). 

This is an ambitious target, so I will work towards it in steps. The planned outline at present is:
1. Encode the rules of chess into an environment
2. Train a deep Q learning for the simpler game of noughts & crosses
3. Apply the deep Q learning model to the chess environment
4. Evaluate and decide next steps.

## Results so far

#### ✅ Define the rules of chess
I coded up an object-oriented chess environment. The ChessBoard object can print out the current state of the board. Check out this image showing a game the computer played against itself - White eventually won after ~50 moves, checkmating Black! Note I'm using the chess notations of e.g. K for King, Q for Queen, etc..

![alt text](https://github.com/rvbrooks/chess_engine/blob/main/images/chess_rules.png)

  - *Status*: 
       - ✅ The computer can play a completely random game against itself, with support for the special move cases of castling, en-passant and pawn promotion
       - ✅ The board state and board square control can be printed out for each move in the game.

#### ✅ Implement deep Q learning for Noughts & Crosses
Since chess is quite a complex game, I first implemented deep reinforcement learning for noughts (O) & crosses (X) (tic-tac-toe for Americans).

When training a deep learning (X's) vs a random opponent (O's), the X player clearly starts to beat the random O player every time after several 1000 epochs of training. In fact, the deep learner wins >99% of games versus the random player, when placing first.
![alt text](https://github.com/rvbrooks/chess_engine/blob/main/images/nc_learning.png)

- ✅ Winrate for a trained policy when going first vs a randomly acting opponent is ~99%, which is best expected.
- ✅ Winrate for a trained policy when going second vs a randomly acting opponent is ~82%, which is best expected.
- ✅ Implemented learning through self play against another learner.

#### ☐ Apply simple deep reinforcement model to chess

## Project Structure
```
chess_engine
├── docs   
├── src 
├── test
├── tools
└── README.md
```
