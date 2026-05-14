from board_definition import ROWS, SPACING

class BoardRenderer:

    def render(self, board):

        BLUE = "\033[94m"
        RED = "\033[91m"
        RESET = "\033[0m"

        print ()

        for row, tiles in ROWS.items():

            print(" " * SPACING[row], end="")

            for label, coord in tiles:

                occupant = board.get(coord)

                if occupant == None:
                    text = label

                elif occupant == 1:
                    text = f"{BLUE}{label}{RESET}"

                elif occupant == 2:
                    text = f"{RED}{label}{RESET}"

                else:
                    text = "??"

                print(f"{text} ", end="")

            print()

        print()