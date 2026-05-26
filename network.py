import json

def send_json(conn, data):

    message = json.dumps(data) + "\n"

    conn.send(message.encode())