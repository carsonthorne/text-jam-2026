import threading
import time

from chinese_checkers.game.game_state import GameState
from chinese_checkers.shared.network import send_json, safe_send_json
from chinese_checkers.game.move_validator import validate_partial_move, validate_move
from chinese_checkers.server.session_states import LOBBY, IN_PROGRESS
from chinese_checkers.shared.messages import (
    make_game_state,
    make_lobby_state,
    make_error,
    make_partial_validation,
    make_game_started,
    make_player_joined_game
)
from chinese_checkers.shared.message_types import (
    ERROR,
    VALIDATE_PARTIAL,
    MOVE,
    START_GAME,
    UPDATE_NUM_PLAYERS,
    LEAVE_LOBBY
)

RECONNECT_TIMEOUT = 300      # Clean up session after five minutes of inactivity.

class Session:

    def __init__(self, session_id, num_players):
        self.session_id = session_id
        
        self.lobby_num_players = num_players
        self.game_num_players = None

        self.players = {}

        self.host_player_id = None

        self.game_state = None

        self.lock = threading.Lock()

        self.state = LOBBY

        self.created_at = time.time()
        self.last_activity = time.time()

        self.message_handlers = {
            VALIDATE_PARTIAL: self._handle_validate_partial,
            MOVE: self._handle_move_message,
            START_GAME: self._handle_start_game_message,
            UPDATE_NUM_PLAYERS: self._handle_update_num_players,
            LEAVE_LOBBY: self._handle_leave_lobby
        }


    def add_player(self, player):
        
        self.touch()
        
        if not self.host_player_id:
            self.host_player_id = player.player_id

        self.players[player.player_id] = player

        self.broadcast_lobby_state()

        return True


    def remove_player(self, player):

        if player.player_id not in self.players:
            return

        was_host = player.player_id == self.host_player_id

        del self.players[player.player_id]

        if was_host:

            self.host_player_id = None

            if self.players:

                self.host_player_id = next(
                    iter(self.players.values())
                ).player_id

        self.broadcast_lobby_state()

        print(
            f"Player {player.player_id} left session "
            f"{self.session_id}"
        )


    def assign_player_numbers(self):
        for i, player in enumerate(self.players.values(), start=1):
            player.player_number = i


    def get_connected_players(self):

        return [
            player.player_id
            for player in self.players.values()
            if player.connected
        ]


    def get_player_num(self, player_id):

        for player in self.players.values():

            if player.player_id == player_id:

                return player.player_number

        return None


    def serialize_players(self):

        return [
            {
                "name": player.name,
                "player_number": player.player_number,
                "connected": player.connected,
                "is_host": player.player_id == self.host_player_id
            }
            for player in self.players.values()
        ]
    

    def handle_disconnect(self, player):

        player.disconnect()

        self.broadcast_lobby_state()

        print(
            f"session.py: handle_disconnect(): Player {player.player_number} disconnected "
            f"from session {self.session_id}"
        )


    def has_disconnected_players(self):

        return any(
            not player.connected
            for player in self.players.values()
        )
    

    def touch(self):

        self.last_activity = time.time()
    

    def is_abandoned(self):

        now = time.time()

        for player in self.players.values():

            if player.connected:
                return False
            
            if now - player.last_seen < RECONNECT_TIMEOUT:
                return False
            
        return True


    def broadcast_lobby_state(self):

        for player in self.players.values():

            if player.connected and player.connection:

                safe_send_json(player, make_lobby_state(self, player))


    def broadcast_game_state(self):

        for player in self.players.values():

            if player.connected and player.connection:

                safe_send_json(player, make_game_state(self.game_state))


    def start_game(self):

        self.game_num_players = len(self.players)

        self.assign_player_numbers()

        print("START GAME: ", self.game_num_players)

        self.game_state = GameState(self.game_num_players)

        self.state = IN_PROGRESS

        for player in self.players.values():
            print(f"Player {player.name} has number {player.player_number}")
            if player.connected:

                safe_send_json(player, make_game_started(self, player))

                for joined_player in self.players.values():

                    safe_send_json(player, make_player_joined_game(joined_player))

        self.broadcast_game_state()


    def handle_message(self, player, data):

        message_type = data.get("type")

        handler = self.message_handlers.get(message_type)

        if handler:

            handler(player, data)


    def _handle_start_game_message(self, player, data=None):

        if player.player_id != self.host_player_id:
            return

        if len(self.players) != self.lobby_num_players:

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


    def _handle_update_num_players(self, player, data):

        if player.player_id != self.host_player_id:
            return

        self.lobby_num_players = data["num_players"]

        self.broadcast_lobby_state()


    def _handle_leave_lobby(self, player, data):

        if self.state != LOBBY:
            return

        self.remove_player(player)

        player.disconnect()

        if player.connection:

            try:
                player.connection.close()
            except:
                pass
    

    def validate_partial_selection(self, player, path):

        with self.lock:

            valid, reason = validate_partial_move(
                self.game_state.board,
                player.player_number,
                path
            )

        return make_partial_validation(valid, reason)


    def handle_move(self, player, path):

        if self.state != IN_PROGRESS:

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
