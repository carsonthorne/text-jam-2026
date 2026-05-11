import socket
import threading
import json
from game_state import GameState

HOST = "127.0.0.1"
PORT = 5555

clients = []
game_state = GameState()
game_lock = threading.Lock()


def send_json(conn, data):
    message = json.dumps(data) + "\n"
    conn.send(message.encode())

def broadcast_game_state():

    with game_lock:

        state_message = {
            "type": "game_state",
            "board": game_state.serialize_board(),
            "current_player": game_state.current_player + 1
        }

    for client in clients:
        send_json(client, state_message)

def handle_client(conn, player_id):

    send_json(conn, {
        "type": "welcome",
        "player_id": player_id + 1
    })

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

                # Player attempting move
                if data["type"] == "move":

                    with game_lock:

                        if player_id != game_state.current_player:

                            send_json(conn, {
                                "type": "error",
                                "message": "Not your turn."
                            })

                            continue

                        move_from = tuple(data["from"])
                        move_to = tuple(data["to"])

                        valid, reason = game_state.is_valid_move(
                            player_id,
                            move_from,
                            move_to
                        )

                        if not valid:

                            send_json(conn, {
                                "type": "error",
                                "message": reason
                            })

                            continue

                        game_state.apply_move(move_from, move_to)

                    broadcast_game_state()

        except Exception as e:
            print("Error:", e)
            break

    conn.close()


def start_server():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind((HOST, PORT))
    server.listen(2)

    print("Waiting for players...")

    while len(clients) < 2:
        conn, addr = server.accept()
        print(f"Connected: {addr}")
        clients.append(conn)

    for i, conn in enumerate(clients):
        thread = threading.Thread(target=handle_client, args=(conn, i))
        thread.start()

    print("Game starting!")
    broadcast_game_state()


if __name__ == "__main__":
    start_server()