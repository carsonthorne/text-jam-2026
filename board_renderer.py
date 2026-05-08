class BoardRenderer:

    def __init__(self):

        self.rows = {
            "A": ["A1"],
            "B": ["B1", "B2"],
            "C": ["C1", "C2", "C3"],
            "D": ["D1", "D2", "D3", "D4"],
            "E": ["E1", "E2", "E3", "E4", "E5"],
            "F": ["F1", "F2", "F3", "F4", "F5", "F6"],
            "G": ["G1", "G2", "G3", "G4", "G5", "G6", "G7"]
        }

        self.spacing = {
            "A": 12,
            "B": 10,
            "C": 8,
            "D": 6,
            "E": 4,
            "F": 2,
            "G": 0
        }

    def render(self, board):

        print ()

        for row, tiles in self.rows.items():

            print(" " * self.spacing[row], end="")

            for tile in tiles:

                occupant = board.get(tile)

                if occupant is None:
                    symbol = "○"

                elif occupant == 1:
                    symbol = "●"    #blue

                elif occupant == 2:
                    symbol = "\033[91m●\033[0m"    #red

                else:
                    symbol = "?"

                print(f"{tile}:{symbol} ", end="")

            print()

        print()