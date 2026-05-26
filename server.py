import socket
import threading
import json
import traceback
import time

from player import Player
from session_manager import SessionManager
from session import Session
from network import send_json

HOST = "127.0.0.1"
PORT = 5555


manager = SessionManager()

def handle_connection(manager, conn):

    buffer = ""

    chunk = conn.recv(1024).decode()

    buffer += chunk

    line, buffer = buffer.split("\n", 1)

    data = json.loads(line)

    if data["type"] != "connect":
        conn.close()
        return

    player_id = data["player_id"]

    session_id = data.get("session_id")

    if session_id:

        session = manager.get_session(session_id)

        if session is None:

            send_json(conn, {
                "type": "error",
                "message": "Session not found."
            })

            conn.close()
            return
        
        print(f"Player connected to session {session.session_id}")
        
    else:

        session = manager.create_session(2)

        session_id = session.session_id

        print(f"Created session {session.session_id}")

    # Reconnect player
    if player_id in session.players:

        player = session.players[player_id]
        player.attach_connection(conn)
        player.connected = True
        player.last_seen = time.time()

    # New players
    else:
        if len(session.players) >= session.num_players:
            conn.close()
            return

        player_number = session.assign_player_number()
        if player_number is None:
            conn.close()
            return

        player = Player( player_id, player_number, data["name"], session.session_id)

        player.attach_connection(conn)

        session.add_player(player)

    send_json(conn, {
        "type": "welcome",
        "player_number": player.player_number,
        "players": session.game_state.players,
        "session_id": session.session_id
    })

    send_json(conn, {
        "type": "game_state",
        "board": session.game_state.serialize_board(),
        "current_player": session.game_state.current_player_number,
        "winner": session.game_state.winner,
    })

    if len(session.players) == session.num_players and all(p.connected for p in session.players.values()):

        print("Game starting!")

        session.start_game()

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

                    path = [tuple(coord) for coord in data["path"]]

                    response = session.validate_partial_selection(player, path)

                    send_json(conn, response)

                    continue

                # Player submitting move
                if data["type"] == "move":

                    path = [tuple(coord) for coord in data["path"]]

                    result = session.handle_move(player, path)

                    if not result["success"]:
                        send_json(conn, result["response"])

        except Exception as e:
            # print("Error:", e)
            traceback.print_exc()
            break

    session.handle_disconnect(player)

    conn.close()

    print(f"Player {player.player_number} disconnected")

def start_server():

    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind((HOST, PORT))
    server.listen()

    print("Waiting for players...")

    while True:

        conn, addr = server.accept()

        print(f"Connected: {addr}")

        thread = threading.Thread(
            target=handle_connection,
            args=(manager, conn)
        )

        thread.start()

if __name__ == "__main__":
    start_server()