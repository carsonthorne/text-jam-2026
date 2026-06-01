import json

MAX_MESSAGE_SIZE = 8192

def send_json(conn, data):

    message = json.dumps(data) + "\n"

    conn.send(message.encode())


def receive_json(conn, buffer):
    
    while "\n" not in buffer:

        chunk = conn.recv(1024).decode()

        if not chunk:
            return None, buffer
        
        buffer += chunk

        if len(buffer) > MAX_MESSAGE_SIZE:

            raise ValueError("Message exceeds maximum size")

    line, buffer = buffer.split("\n", 1)

    return json.loads(line), buffer


def safe_send_json(player, data):

    if not player.connected or not player.connection:
        return False
    
    try:

        send_json(player.connection, data)
        return True
    
    except OSError:

        player.disconnect()
        return False