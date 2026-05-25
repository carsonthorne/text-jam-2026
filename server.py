import socket
import threading
import json
import traceback
import time
from game_state import GameState
from move_validator import validate_partial_move, validate_move
from player import Player

HOST = "127.0.0.1"
PORT = 5555

num_players = 2

players = {}
game_state = None
game_lock = threading.Lock()


def send_json(conn, data):
    message = json.dumps(data) + "\n"
    conn.send(message.encode())

def broadcast_game_state():

    with game_lock:

        state_message = {
            "type": "game_state",
            "board": game_state.serialize_board(),
            "current_player": game_state.current_player_number,
            "winner": game_state.winner,
        }

    for player in players.values():

        if player.connected and player.connection:

            send_json(player.connection, state_message)

def handle_connection(conn):

    buffer = ""

    chunk = conn.recv(1024).decode()

    buffer += chunk

    line, buffer = buffer.split("\n", 1)

    data = json.loads(line)

    if data["type"] != "connect":
        conn.close()
        return

    player_id = data["player_id"]

    # Reconnect player
    if player_id in players:
        player = players[player_id]
        player.attach_connection(conn)
        player.connected = True
        player.last_seen = time.time()

    # New players
    else:
        if len(players) >= num_players:
            conn.close()
            return

        player_number = assign_player_number()
        if player_number is None:
            conn.close()
            return

        player = Player( player_id, player_number, data["name"])

        player.attach_connection(conn)

        players[player_id] = player

        # print("PLAYER STATE:")
        # for p in players.values():
        #     print(
        #         p.player_id,
        #         p.connected
        #     )


    send_json(conn, {
        "type": "welcome",
        "player_number": player.player_number,
        "players": game_state.players
    })

    send_json(conn, {
        "type": "game_state",
        "board": game_state.serialize_board(),
        "current_player": game_state.current_player_number,
        "winner": game_state.winner,
    })

    if len(players) == num_players and all(p.connected for p in players.values()):


        # print("GAME STATE CHECK:")
        # print("Players:")
        # for p in players.values():
        #     print(p.player_number, p.player_id, p.connected)

        # print("GameState players:")
        # print(game_state.players)


        print("Game starting!")

        broadcast_game_state()

    buffer = ""

    while True:
        try:
            chunk = conn.recv(1024).decode()

            if not chunk:
                break

            buffer += chunk

            while "\n" in buffer:

                line, buffer = buffer.split("\n", 1)

                if not line:
                    continue

                data = json.loads(line)

                # Player making selection
                if data["type"] == "validate_partial":

                    with game_lock:

                        path = [tuple(coord) for coord in data["path"]]

                        valid, reason = validate_partial_move(
                            game_state.board,
                            player.player_number,
                            path
                        )

                    send_json(conn, {
                        "type": "partial_validation",
                        "valid": valid,
                        "message": reason
                    })

                    continue

                # Player submitting move
                if data["type"] == "move":

                    with game_lock:

                        if not game_state.is_players_turn(player.player_number):

                            send_json(conn, {
                                "type": "error",
                                "message": "Not your turn."
                            })

                            continue

                        path = [tuple(coord) for coord in data["path"]]

                        valid, reason = validate_move(
                            game_state.board,
                            game_state.players,
                            player.player_number,
                            path
                        )

                        if not valid:

                            send_json(conn, {
                                "type": "error",
                                "message": reason
                            })

                            continue

                        game_state.apply_move(path[0], path[-1])

                    broadcast_game_state()

        except Exception as e:
            # print("Error:", e)
            traceback.print_exc()
            break

    player.disconnect()

    conn.close()

    print(f"Player {player.player_number} disconnected")

def assign_player_number():
    used = {p.player_number for p in players.values()}
    for i in range(1, num_players + 1):
        if i not in used:
            return i
    return None

def start_server():

    global game_state

    game_state = GameState(num_players)

    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind((HOST, PORT))
    server.listen(num_players)

    print("Waiting for players...")

    while True:

        conn, addr = server.accept()

        print(f"Connected: {addr}")

        thread = threading.Thread(
            target=handle_connection,
            args=(conn,)
        )

        thread.start()

if __name__ == "__main__":
    start_server()