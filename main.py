import os
import sys
pwd = os.path.dirname(__file__)
print(pwd)
sys.path.append(pwd+r"\\src")
for p in sys.path:
    print(p)

print(os.getcwd())

from chess_environment import ChessBoard

if __name__ == "__main__":
    cb = ChessBoard()
    cb.perspective = 0

    cb.play_game(500, perspective=0, wait=0)
