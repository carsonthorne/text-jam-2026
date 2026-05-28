import socket
import threading
import traceback
import time

from player import Player
from session_manager import SessionManager
from network import send_json, receive_json
from message_types import (
    CONNECT,
    WELCOME,
    WAITING_FOR_PLAYERS,
    GAME_STATE,
    ERROR,
    RECONNECTED,
    DEBUG
)

HOST = "127.0.0.1"
PORT = 5555


manager = SessionManager()

def handle_connection(manager, conn):

    buffer = ""

    data, buffer = receive_json(conn, buffer)

    if data is None:
        conn.close()
        return

    if data["type"] != CONNECT:
        conn.close()
        return

    player_id = data["player_id"]

    session_id = data.get("session_id")

    if session_id:

        session = manager.get_session(session_id)

        if session is None:

            send_json(conn, {
                "type": ERROR,
                "message": "Session not found."
            })

            conn.close()
            return
        
        print(f"Player connected to session {session.session_id}")
        
    else:

        num_players = data.get("num_players", 2)

        session = manager.create_session(num_players)

        session_id = session.session_id

        print(f"Created session {session.session_id}")


    # Reconnect player
    if player_id in session.players:

        player = session.players[player_id]
        player.attach_connection(conn)
        player.reconnect(conn)
        session.broadcast_lobby_state()
        player.last_seen = time.time()
        session.touch()

        send_json(conn, {"type": RECONNECTED})


    # New players
    else:
        if len(session.players) >= session.num_players:
            send_json(conn, {
                "type": ERROR,
                "message": "Session is full."
            })
            conn.close()
            return

        player_number = session.assign_player_number()
        if player_number is None:
            send_json(conn, {
                "type": ERROR,
                "message": "Session is full."
            })
            conn.close()
            return

        player = Player( player_id, player_number, data["name"], session.session_id)

        player.attach_connection(conn)

        session.add_player(player)


    send_json(conn, {
        "type": WELCOME,
        "player_number": player.player_number,
        "players": session.game_state.players,
        "session_id": session.session_id
    })

    if session.state == "lobby":
        send_json(conn, {"type": WAITING_FOR_PLAYERS})

    send_json(conn, {
        "type": GAME_STATE,
        "board": session.game_state.serialize_board(),
        "current_player": session.game_state.current_player_number,
        "winner": session.game_state.winner,
    })

    buffer = ""


    # Receive message loop
    while True:
        try:

            data, buffer = receive_json(conn, buffer)

            if data is None:
                break

            if data["type"] == DEBUG:
                
                print("DEBUG: ", data["message"])
                
                continue

            session.handle_message(player, data)

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

    cleanup_thread = threading.Thread(
        target=cleanup_loop,
        daemon=True
    )

    cleanup_thread.start()

    print("Waiting for players...")

    while True:

        conn, addr = server.accept()

        print(f"Connected: {addr}")

        thread = threading.Thread(
            target=handle_connection,
            args=(manager, conn)
        )

        thread.start()


def cleanup_loop():

    while True:

        manager.cleanup_sessions()

        time.sleep(10)

if __name__ == "__main__":
    start_server()