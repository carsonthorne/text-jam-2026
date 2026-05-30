import socket
import threading
import traceback
import time

from player import Player
from session_manager import SessionManager
from network import send_json, receive_json
from messages import (
    make_welcome,
    make_error,
    make_game_state,
    make_reconnected,
    make_invalid_session,
    make_session_validated,
    make_duplicate_player
)
from message_types import (
    CONNECT,
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
    session = None

    # Identity file has session id
    if session_id:

        session = manager.get_session(session_id)

        # Session ID belongs to expired / invalid session.
        if session is None:
            send_json(conn, make_invalid_session())
            conn.close()
            return


        session_players = session.get_connected_players()

        # Trying to connect to session while already connected (Duplicate player).
        if player_id in session_players:
            send_json(conn, make_duplicate_player())
            conn.close()
            return

        # Session is valid
        player_num = session.get_player_num(player_id)
        send_json(conn, make_session_validated(session, player_num))


    # Player created a new session
    if session is None:
        num_players = data.get("num_players", 2)
        session = manager.create_session(num_players)
        session_id = session.session_id


    # Reconnect player to valid session
    if player_id in session.players:

        player = session.players[player_id]
        player.attach_connection(conn)
        session.broadcast_lobby_state()
        player.last_seen = time.time()
        session.touch()

        print(f"\nPlayer id {player_id} reconnected to Session id: {session.session_id}")
        send_json(conn, make_welcome(player, session))
        send_json(conn, make_reconnected())


    # New player connecting to session
    else:
        player_number = session.assign_player_number()
        if player_number is None:
            print("SERVER: FAILED TO ASSIGN NUMBER")
            send_json(conn, make_error("Session is full."))
            conn.close()
            return

        player = Player( player_id, player_number, data["name"], session.session_id)
        player.attach_connection(conn)
        session.add_player(player)
        print(f"\nPlayer id: {player_id} connected to Session id: {session.session_id}")
        send_json(conn, make_welcome(player, session))

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
            print("\nError: server receive loop:", e)
            traceback.print_exc()
            break

    session.handle_disconnect(player)

    conn.close()

    print(f"Server.py: Player {player.player_id} disconnected")


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

    print("Server.py: Server started")

    while True:

        conn, addr = server.accept()

        print(f"Server.py: New connection: {addr}")

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