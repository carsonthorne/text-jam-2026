class BoardRenderer:

    def __init__(self):

        self.rows = {
            "A": [("A1", (0,0))],
            "B": [
                ("B1", (-1,1)),
                ("B2", (0,1))
                ],
            "C": [
                ("C1", (-2,2)),
                ("C2", (-1,2)),
                ("C3", (0,2))
                ],
            "D": [
                ("D1", (-3,3)),
                ("D2", (-2,3)),
                ("D3", (-1,3)),
                ("D4", (0,3))
                ],
            "E": [
                ("E1", (-4,4)),
                ("E2", (-3,4)),
                ("E3", (-2,4)),
                ("E4", (-1,4)),
                ("E5", (0,4))
                ],
            "F": [
                ("F1", (-5,5)),
                ("F2", (-4,5)),
                ("F3", (-3,5)),
                ("F4", (-2,5)),
                ("F5", (-1,5)),
                ("F6", (0,5))
                ],
            "G": [
                ("G1", (-6,6)),
                ("G2", (-5,6)),
                ("G3", (-4,6)),
                ("G4", (-3,6)),
                ("G5", (-2,6)),
                ("G6", (-1,6)),
                ("G7", (0,6))
                ]
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

        self.label_to_coord = {}
        self.coord_to_label = {}

        for row, tiles in self.rows.items():

            for label, coord in tiles:

                self.label_to_coord[label] = coord
                self.coord_to_label[coord] = label

    def get_coord(self, label):
        return self.label_to_coord.get(label)
    
    def get_label(self, coord):
        return self.coord_to_label.get(coord)

    def render(self, board):

        print ()

        for row, tiles in self.rows.items():

            print(" " * self.spacing[row], end="")

            for label, coord in tiles:

                occupant = board.get(coord)

                if occupant is None:
                    symbol = "○"

                elif occupant == 1:
                    symbol = "●"    #blue

                elif occupant == 2:
                    symbol = "\033[91m●\033[0m"    #red

                else:
                    symbol = "?"

                print(f"{label}:{symbol} ", end="")

            print()

        print()