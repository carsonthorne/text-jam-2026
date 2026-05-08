class GameState:

    def __init__(self):

        self.board = {}

        self.current_player = 0

        self.initialize_board()

    def initialize_board(self):

        # TEMPORARY SIMPLE SETUP
        self.board = {

            "A1": 1,

            "B1": 1,
            "B2": None,

            "C1": None,
            "C2": None,
            "C3": None,

            "D1": None,
            "D2": None,
            "D3": None,
            "D4": None,

            "E1": None,
            "E2": None,
            "E3": None,
            "E4": None,
            "E5": None,

            "F1": None,
            "F2": None,
            "F3": None,
            "F4": None,
            "F5": None,
            "F6": 2,

            "G1": None,
            "G2": None,
            "G3": None,
            "G4": None,
            "G5": None,
            "G6": 2,
            "G7": None
        }

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

        # TODO:
        # Add actual Chinese Checkers rules later ( adjacency/jump rules )

        return True, ""
    

    def apply_move(self, move_from, move_to):

        self.board[move_to] = self.board[move_from]

        self.board[move_from] = None

        self.current_player = 1 - self.current_player

    def get_board_state(self):

        return self.board.copy()