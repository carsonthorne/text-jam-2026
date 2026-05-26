import json

def send_json(conn, data):

    message = json.dumps(data) + "\n"

    conn.send(message.encode())

def receive_json(conn, buffer):
    
    while "\n" not in buffer:

        chunk = conn.recv(1024).decode()

        if not chunk:
            return None, buffer
        
        buffer += chunk

    line, buffer = buffer.split("\n", 1)

    return json.loads(line), buffer