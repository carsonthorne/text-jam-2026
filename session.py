import threading
import time
from game_state import GameState
from network import send_json
from move_validator import validate_partial_move, validate_move

RECONNECT_TIMEOUT = 60      # Clean up session after one minute.

class Session:

    def __init__(self, session_id, num_players):
        self.session_id = session_id
        self.num_players = num_players

        self.players = {}

        self.game_state = GameState(num_players)

        self.lock = threading.Lock()

        self.state = "lobby"

        self.created_at = time.time()
        self.last_activity = time.time()

    def broadcast_game_state(self):

        state_message = {
            "type": "game_state",
            "board": self.game_state.serialize_board(),
            "current_player": self.game_state.current_player_number,
            "winner": self.game_state.winner
        }

        for player in self.players.values():

            if player.connected and player.connection:

                send_json(player.connection, state_message)

    def add_player(self, player):
        
        self.touch()

        if len(self.players) >= self.num_players:
            return False
        
        self.players[player.player_id] = player

        self.broadcast_lobby_state()

        return True
    
    def touch(self):

        self.last_activity = time.time()

    def can_start(self):
        return len(self.players) == self.num_players


    def assign_player_number(self):

        used = {
            p.player_number
            for p in self.players.values()
        }

        for i in range(1, self.num_players + 1):

            if i not in used:
                return i
        
        return None
    
    def validate_partial_selection(self, player, path):

        with self.lock:

            valid, reason = validate_partial_move(
                self.game_state.board,
                player.player_number,
                path
            )

        return {
            "type": "partial_validation",
            "valid": valid,
            "message": reason
        }
    
    def handle_move(self, player, path):

        if self.state != "in_progress":

            return {
                "success": False,
                "response": {
                    "type": "error",
                    "message": "Game is not active."
                }
            }

        with self.lock:

            if not self.game_state.is_players_turn(player.player_number):

                return {
                    "success": False,
                    "response": {
                        "type": "error",
                        "message": "Not your turn."
                    }
                }
            
            valid, reason = validate_move(
                self.game_state.board,
                self.game_state.players,
                player.player_number,
                path
            )

            if not valid:

                return {
                    "success": False,
                    "response": {
                        "type": "error",
                        "message": reason
                    }
                }
            
            self.game_state.apply_move(
                path[0],
                path[-1]
            )

        self.touch()

        self.broadcast_game_state()

        return {"success": True}
    
    def handle_disconnect(self, player):

        player.disconnect()

        self.broadcast_lobby_state()

        print(
            f"Player {player.player_number} disconnected "
            f"from session {self.session_id}"
        )

    def has_disconnected_players(self):

        return any(
            not player.connected
            for player in self.players.values()
        )
    
    def is_abandoned(self):

        now = time.time()

        for player in self.players.values():

            if player.connected:
                return False
            
            if now - player.last_seen < RECONNECT_TIMEOUT:
                return False
            
        return True
    
    def serialize_players(self):

        return [
            {
                "name": player.name,
                "player_number": player.player_number,
                "connected": player.connected,
                "is_host": player.player_number == 1
            }
            for player in self.players.values()
        ]


    def broadcast_lobby_state(self):

        message = {
            "type": "lobby_state",
            "players": self.serialize_players(),
            "session_id": self.session_id,
            "num_players": self.num_players
        }

        for player in self.players.values():

            if player.connected and player.connection:

                # self.app.client.send(player.connection, message)
                send_json(player.connection, message)


    def start_game(self):
        self.state = "in_progress"


        for player in self.players.values():
            
            if player.connected:

                send_json(player.connection, {"type": "game_started"})

        self.broadcast_game_state()