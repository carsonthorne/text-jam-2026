import socket
import threading
import json
from board_renderer import BoardRenderer

HOST = "127.0.0.1"
PORT = 5555

turn_event = threading.Event()
renderer = BoardRenderer()
board = {}
player_id = None


def send_json(client, data):
    message = json.dumps(data) + "\n"
    client.send(message.encode())


def receive_messages(client):

    buffer = ""

    while True:
        try:
            chunk = client.recv(1024).decode()

            if not chunk:
                break

            buffer += chunk

            while "\n" in buffer:

                line, buffer = buffer.split("\n", 1)

                if not line:
                    continue

                data = json.loads(line)

                msg_type = data["type"]

                if msg_type == "welcome":

                    global player_id

                    player_id = data["player_id"]

                    print(f"You are Player {player_id}")

                elif msg_type == "game_state":

                    global board

                    serialized_board = data["board"]

                    board = {}

                    for key, value in serialized_board.items():

                        q, r = map(int, key.split(","))

                        board[(q, r)] = value

                    print("\nUpdated Board:")
                    renderer.render(board)

                    if data["current_player"] == player_id:
                        print("\nYour turn!")
                        turn_event.set()
                    else:
                        print("\nWaiting for opponent...")
                        turn_event.clear()

                elif msg_type == "error":
                    print("\nERROR:", data["message"])
                    turn_event.set()

        except Exception as e:
            print("Connection closed:", e)
            break


def input_loop(client):

    while True:

        # Sleep until your turn
        turn_event.wait()

        move = input("Enter move (example B2 D4): ")

        try:
            move_from, move_to = move.split()

            move_from_coord = renderer.get_coord(move_from)
            move_to_coord = renderer.get_coord(move_to)

            if move_from_coord is None or move_to_coord is None:
                print("Invalid Tile.")
                continue

            send_json(client, {
                "type": "move",
                "from": move_from_coord,
                "to": move_to_coord
            })

            # Prevent multiple moves
            turn_event.clear()

        except:
            print("Invalid input format.")


def start_client():
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect((HOST, PORT))

    receive_thread = threading.Thread(
        target=receive_messages,
        args=(client,),
        daemon=True
    )

    receive_thread.start()

    input_loop(client)


if __name__ == "__main__":
    start_client()