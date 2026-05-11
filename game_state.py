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

        self.initialize_board()

    def initialize_board(self):

        for r in range(7):

            for q in range(-r, 1):

                self.board[(q, r)] = None

        #TEMP pieces
        self.board[(0, 0)] = 1

        self.board[(0, 1)] = 1

        self.board[(0, 5)] = 2
        self.board[(-1, 5)] = 2

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

    def is_valid_move(self, player_id, move_from, move_to):

        # Is source tile valid?
        if move_from not in self.board:
            return False, "Invalid source tile."

        # Is source tile valid?
        if move_to not in self.board:
            return False, "Invalid destination tile."
        
        # Is there actually a piece there?
        if self.board[move_from] is None:
            return False, "No piece there."

        # Is it player's piece?
        if self.board[move_from] != player_id + 1:
            return False, "Not your piece."

        # Is destination occupied?
        if self.board[move_to] is not None:
            return False, "Destination occupied."

        if self.is_adjacent_move(move_from, move_to):
            return True, ""
        
        if self.is_jump_move(move_from, move_to):
            return True, ""
        
        return False, "Illegal move."
            
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