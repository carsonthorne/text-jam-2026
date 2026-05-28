import threading
import time

from game_state import GameState
from network import send_json, safe_send_json
from move_validator import validate_partial_move, validate_move
from messages import make_game_state, make_lobby_state, make_error
from message_types import (
    GAME_STARTED,
    PARTIAL_VALIDATION,
    ERROR,
    VALIDATE_PARTIAL,
    MOVE,
    START_GAME
)

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

        self.message_handlers = {
            VALIDATE_PARTIAL: self._handle_validate_partial,
            MOVE: self._handle_move_message,
            START_GAME: self._handle_start_game_message
        }


    def broadcast_game_state(self):

        for player in self.players.values():

            if player.connected and player.connection:

                safe_send_json(player, make_game_state(self.game_state))


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
            "type": PARTIAL_VALIDATION,
            "valid": valid,
            "message": reason
        }
    

    def handle_move(self, player, path):

        if self.state != "in_progress":

            return {
                "success": False,
                "response": {
                    "type": ERROR,
                    "message": "Game is not active."
                }
            }

        with self.lock:

            if not self.game_state.is_players_turn(player.player_number):

                return {
                    "success": False,
                    "response": {
                        "type": ERROR,
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
                        "type": ERROR,
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

        for player in self.players.values():

            if player.connected and player.connection:

                safe_send_json(player, make_lobby_state(self))


    def start_game(self):
        self.state = "in_progress"


        for player in self.players.values():
            
            if player.connected:

                safe_send_json(player, {"type": GAME_STARTED})

        self.broadcast_game_state()


    def _handle_start_game_message(self, player, data=None):

        if player.player_number != 1:

            safe_send_json(player, make_error("Only the host can start the game."))

            return

        if len(self.players) != self.num_players:

            safe_send_json(player, make_error("Not enough players."))

            return

        self.start_game()


    def _handle_validate_partial(self, player, data):

        path = [tuple(coord) for coord in data["path"]]

        response = self.validate_partial_selection(
            player,
            path
        )

        send_json(player.connection, response)


    def _handle_move_message(self, player, data):

        path = [tuple(coord) for coord in data["path"]]

        result = self.handle_move(player, path)

        if not result["success"]:

            send_json(
                player.connection,
                result["response"]
            )


    def handle_message(self, player, data):

        message_type = data.get("type")

        handler = self.message_handlers.get(message_type)

        if handler:

            handler(player, data)