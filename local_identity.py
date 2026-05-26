import json
import uuid
from pathlib import Path

IDENTIFY_FILE = Path.home() / ".chinese_checkers_identity.json"


def load_identity(force_new=False):

    if not force_new and IDENTIFY_FILE.exists():

        with open(IDENTIFY_FILE, "r") as f:
            return json.load(f)
    
    session_id = input(
        "Enter session ID (blank to create new session): "
    ).strip()

    # Assign a universally unique id
    identity = {
        "player_id": str(uuid.uuid4()),
        "session_id": session_id or None,
        "name": input("Enter your name: ")
    }

    with open(IDENTIFY_FILE, "w") as f:
        json.dump(identity, f)

    return identity

def save_identity(identity):

    with open(IDENTIFY_FILE, "w") as f:
        json.dump(identity, f)