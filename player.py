from socket import socket
from sys import platform, argv
from os import system
from json import loads
CLEAR = "clear" if platform == "Darwin" else "cls"
PORT = 40676 + int(argv[1])
player = socket()
PIECES = ["X", "O"]
MOVE_FLAG = 0xF0.to_bytes()

def display_board(moves):
    for cell in range(9):
        char = str(cell)
        try:
            pos = moves.index(cell)
            char = PIECES[pos % 2]
        except:
            pass
        print(char, end="|")
        if (cell + 1) % 3 == 0:
            print()
            print("-"*6)

def display_game(msg):
    #system(CLEAR)
    print("received message", msg)
    
    moves, log = msg.split("///")
    moves = loads(moves)

    display_board(moves)
    print(log)
    return moves

def get_move(move_history):    
    valid = False
    while not valid:
        move = input("Enter your move: ")
        if move.isdigit():
            move = int(move)
            if move < 9:
                if move not in move_history:
                    return move
            print("Invalid move.")

def transmit_move(player, move):
    player.send(str(move).encode())

player.connect(('127.0.0.1', PORT))
player.settimeout(100)

game_over = False
msg = player.recv(1024)
print(msg.decode())
while not game_over:
    msg = player.recv(1024).decode()
    if any(end_term in msg for end_term in "draw,WON,lost".split(",")):
        game_over = True
        
    move_history = display_game(msg)
    if not game_over:
        new_move = get_move(move_history)
        display_board(move_history + [new_move])
        print("...waiting for other player...")
        transmit_move(player, new_move)


player.close()
input()