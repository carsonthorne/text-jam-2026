from board_renderer import BoardRenderer

class GameState:

    HEX_DIRECTIONS = [
        (1, 0),
        (1, -1),
        (0, -1),
        (-1, 0),
        (-1, 1),
        (0, 1)
    ]

    def __init__(self):

        self.board = {}

        self.current_player = 0

        self.renderer = BoardRenderer()

        self.initialize_board()

    def initialize_board(self):

        for coord in self.renderer.get_all_coords():
            self.board[coord] = None

        #TEMP pieces

        self.board[(0, 1)] = 1
        self.board[(0, 2)] = 1

        self.board[(0, 4)] = 2
        self.board[(1, 5)] = 2
        self.board[(1, 6)] = 2
        self.board[(-1, 8)] = 2
        self.board[(-3, 10)] = 2
        self.board[(-5, 12)] = 2
        self.board[(-7, 14)] = 2

    def add_coords(self, a, b):
        return (a[0] + b[0], a[1] + b[1])
    
    def is_adjacent_move(self, move_from, move_to):

        for direction in self.HEX_DIRECTIONS:

            neighbor = self.add_coords(move_from, direction)

            if neighbor == move_to:
                return True
        
        return False
    
    def is_jump_move(self, move_from, move_to):

        for direction in self.HEX_DIRECTIONS:

            middle = self.add_coords(move_from, direction)

            landing = self.add_coords(middle, direction)

            if landing == move_to:

                if middle in self.board and self.board[middle] is not None:

                    return True
        
        return False

    def is_valid_move(self, player_id, path):

        if len(path) < 2:
            return False, "Invalid move."
        
        move_from = path[0]
        move_to = path[-1]

        # Is source tile valid?
        if move_from not in self.board:
            return False, "Invalid source tile."

        
        # Is there actually a piece there?
        if self.board[move_from] is None:
            return False, "No piece there."

        # Is it player's piece?
        if self.board[move_from] != player_id + 1:
            return False, "Not your piece."

        # -------------
        # Adjacent move
        # -------------

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
            
        #-----------
        # Jump chain
        #-----------

        visited = set()

        for i in range(len(path) - 1):

            current = path[i]
            nxt = path[i + 1]

            # Prevent loops
            if nxt in visited:
                return False, "Cannot revisit tiles."
            
            visited.add(current)

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
            
    def apply_move(self, move_from, move_to):

        self.board[move_to] = self.board[move_from]

        self.board[move_from] = None

        self.current_player = 1 - self.current_player

    def serialize_board(self):

        serialized = {}

        for coord, value in self.board.items():

            key = f"{coord[0]},{coord[1]}"
            serialized[key] = value

        return serialized