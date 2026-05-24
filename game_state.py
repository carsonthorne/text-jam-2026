from board_layout import (
    VALID_COORDS,
    HEX_DIRECTIONS,
    HOME_ZONES,
)

from player_configs import PLAYER_CONFIGS

class GameState:

    def __init__(self, num_players=2):

        self.num_players = num_players
        self.players = PLAYER_CONFIGS[num_players]

        self.board = {}
        self.current_player_index = 0

        self.winner = None

        self.initialize_board()

    @property
    def current_player(self):
        return self.players[self.current_player_index]
    
    @property
    def current_player_number(self):
        return self.current_player["player"]

    def initialize_board(self):

        for coord in VALID_COORDS:
            self.board[coord] = None

        for config in self.players:

            player_number = config["player"]
            start_zone = config["start"]

            for coord in HOME_ZONES[start_zone]:
                self.board[coord] = player_number

    def check_winner(self, player_number):

        player_config = next(
            p for p in self.players
            if p["player"] == player_number
        )

        target_zone_name = player_config["goal"]

        target_zone = HOME_ZONES[target_zone_name]

        player_positions = {
            coord
            for coord, piece in self.board.items()
            if piece == player_number
        }

        return player_positions == target_zone
    
    def is_players_turn(self, player_number):
        return player_number == self.current_player_number

    def get_zone_for_coord(self, coord):
        for zone_name, coords in HOME_ZONES.items():

            if coord in coords:
                return zone_name
            
        return None
    
    def add_coords(self, a, b):
        return (a[0] + b[0], a[1] + b[1])
    
    def is_adjacent_move(self, move_from, move_to):

        for direction in HEX_DIRECTIONS:

            neighbor = self.add_coords(move_from, direction)

            if neighbor == move_to:
                return True
        
        return False
    
    def is_jump_move(self, move_from, move_to):

        for direction in HEX_DIRECTIONS:

            middle = self.add_coords(move_from, direction)

            landing = self.add_coords(middle, direction)

            if landing == move_to:

                if middle in self.board and self.board[middle] is not None:

                    return True
        
        return False
    
    def is_valid_partial_move(self, player_number, path):

        if len(path) < 1:
            return False, "Invalid selection."
        
        move_from = path[0]

        # Is source tile valid?
        if move_from not in self.board:
            return False, "Invalid source tile."
        
        # Is there actually a piece there?
        if self.board[move_from] is None:
            return False, "No piece there."
        
        # Is it player's piece?
        if self.board[move_from] != player_number:
            return False, "Not your piece."
        
        # Only selecting first tile
        if len(path) == 1:
            return True, ""
        
        # --------------
        # Adjacent move
        # --------------

        if len(path) == 2:

            destination = path[1]

            # Is destination tile valid?
            if destination not in self.board:
                return False, "Invalid destination tile."
            
            # Is destination occupied?
            if self.board[destination] is not None:
                return False, "Destination occupied."
            
            if self.is_adjacent_move(move_from, destination):
                return True, ""
            
        # -----------
        # Jump chain
        # -----------

        visited = {move_from}

        for i in range(len(path) - 1):

            current = path[i]
            nxt = path[i + 1]

            # Prevent loops
            if nxt in visited:
                return False, "Cannot revisit tiles."
            
            visited.add(nxt)

            # Destination must exist
            if nxt not in self.board:
                return False, "Invalid destination tile."
            
            # Destination must be empty
            if self.board[nxt] is not None:
                return False, "Destination occupied."
            
            # Must be a legal jump
            if not self.is_jump_move(current, nxt):
                return False, "Illegal jump."
            
        return True, ""

    def is_valid_move(self, player_number, path):

        if len(path) < 2:
            return False, "Invalid move."
        
        # First validate the actual movement mechanics
        valid, reason = self.is_valid_partial_move(
            player_number,
            path
        )

        if not valid:
            return False, reason
        
        move_from = path[0]
        move_to = path[-1]

        from_zone = self.get_zone_for_coord(move_from)
        to_zone = self.get_zone_for_coord(move_to)

        player_config = next(
            p for p in self.players
            if p["player"] == player_number
        )

        start_zone = player_config["start"]
        target_zone = player_config["goal"]

        # Prevent returning to home triangle
        if from_zone is None and to_zone == start_zone:
            return False, "Cannot return to your starting triangle."
        
        # Prevent landing in non-target triangles
        if to_zone is not None:

            if to_zone != start_zone and to_zone != target_zone:
                return False, "Cannot enter opponent home triangle."
            
        # Once inside target triangle,
        # the piece cannot leave it
        if to_zone is None and from_zone == target_zone:
            return False, "Piece cannot leave goal zone."
        
        return True, ""
            
    def apply_move(self, move_from, move_to):

        player_number = self.board[move_from]

        self.board[move_to] = player_number

        self.board[move_from] = None

        # Check for victory
        if self.check_winner(player_number):
            
            self.winner = player_number

            return
        
        # Next turn

        self.next_turn()

    def next_turn(self):

        self.current_player_index = (
            self.current_player_index + 1
        ) % self.num_players

    def serialize_board(self):

        serialized = {}

        for coord, value in self.board.items():

            key = f"{coord[0]},{coord[1]}"
            serialized[key] = value

        return serialized