from socket import socket
from typing import List
import subprocess

PORT = 40676
W, H = 3, 3
PIECES = ["X", "O"]
MOVE_FLAG = 0xF0
DELIM = "///"

#############################################

def send_message(msg : str,
                 player_connection: socket):
    player_connection.send(msg.encode())

#############################################

def connect_with_players() -> List[socket]:    
    players = []
    player_num = 1
    for _ in range(2):
        idx = player_num - 1
        p = socket()
        p.bind(('', PORT + player_num))
        p.listen(5)
        print(f"Waiting for player {player_num}.")
        conn, addr = p.accept()
        players.append(conn)        
        msg =  f"""Let's play Noughts and Crosses
You are player {player_num}.      
You will play as {PIECES[idx]}"""
        send_message(msg, players[idx])
        player_num += 1
    return players

#############################################

def get_move(player_num: int, 
             current_player: socket) -> str:    
    move = current_player.recv(1).decode()
    print("Received player's move", move)
    return move

#############################################

def transmit_board(player: socket, log: str, moves: List[int]):
    print("sending board")
    send_message(str(moves) + DELIM + log, player)

#############################################

def transmit_end_game(players: List[socket],
                      winner: str,
                      moves: List[int]):
    for player, piece in zip(players, PIECES):
        board = str(moves) + DELIM
        if winner == "D":
            send_message(board + "It was a draw!\n\nThanks for playing.", player)
        elif winner == piece:
            send_message(board + "You won!!!\n\nThanks for playing.", player)
        else:
            send_message(board + "You lost ;'(\n\nThanks for playing.", player)

#############################################

def check_winner(moves: List[int]) -> str:
    # rows
    board = ["" for _ in range(9)]
    for i, m in enumerate(moves):
        board[m] = PIECES[i % 2]
    
    for i in range(0, 9, 3):
        if board[i] == board[i+1] == board[i+2]:
            if board[i]:
                print("row win ")
                return board[i]
    
    for i in range(0, 3):
        if board[i] == board[i+3] == board[i+6]:
            if board[i]:
                print("col win")
                return board[i]
    
    if board[0] == board[4] == board[8]:
        if board[4]:
            print("diag 1 win")
            return board[4]
    
    if board[2] == board[4] == board[6]:
        if board[4]:
            print("diag 2 win")
            return board[4]
    
    if len(moves) == 9:
        print("draw")
        return "D"

    # game continues
    return ""

#############################################

if __name__ == "__main__":
    result = subprocess.run(["ipconfig"], capture_output=True, text=True, check=True)
    print(f"Running noughts and crosses server on {result.stdout}")
    players = connect_with_players()
    winner = ""
    round = 0
    log = "Player 1... your turn."
    moves = []
    while winner == "":
        
        player_index = round % 2
        this_player = player_index + 1
        other_player = int(not player_index) + 1
        current_player = players[player_index]
        transmit_board(current_player, log, moves)
        move = get_move(this_player, current_player)
        log = "Player {this_player} placed a {PIECES[player_index]} in cell {move}."
        moves.append(int(move))                
        round += 1
        winner = check_winner(moves)
        if winner:
            
            transmit_end_game(players, winner, moves)
        else:
            log = f"\n\nPlayer {other_player}... your turn"
