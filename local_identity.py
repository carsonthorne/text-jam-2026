import json
import uuid
from pathlib import Path

IDENTIFY_FILE = Path.home() / ".chinese_checkers_identity.json"


def load_identity(force_new=False):

    if not force_new and IDENTIFY_FILE.exists():

        with open(IDENTIFY_FILE, "r") as f:
            return json.load(f)
    
    # Assign a universally unique id
    identity = {
        "player_id": str(uuid.uuid4()),
        "name": input("Enter your name: ")
    }

    with open(IDENTIFY_FILE, "w") as f:
        json.dump(identity, f)

    return identity