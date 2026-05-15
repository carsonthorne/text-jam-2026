from board_definition import ROWS, SPACING, HOME_POSITIONS, LABEL_TO_HOME_COLOR

class BoardRenderer:

    def render(self, board):

        BLUE = "\033[94m"
        RED = "\033[91m"
        RESET = "\033[0m"

        HOME_COLORS = {
            "N":  "\033[41m",  # red background
            "NE": "\033[40m",  # black background
            "SE": "\033[44m",  # blue background
            "S":  "\033[42m",  # green background
            "SW": "\033[47m",  # white background
            "NW": "\033[43m",  # yellow background
        }

        print ()

        for row, tiles in ROWS.items():

            print(" " * SPACING[row], end="")

            for label, coord in tiles:

                occupant = board.get(coord)

                home_zone = LABEL_TO_HOME_COLOR.get(label)
                bg = HOME_COLORS.get(home_zone, "")

                if occupant == None:
                    text = f"{bg}{label}{RESET}"

                elif occupant == 1:
                    text = f"{bg}{BLUE}{label}{RESET}"

                elif occupant == 2:
                    text = f"{bg}{RED}{label}{RESET}"

                else:
                    text = f"{bg}??{RESET}"

                print(f"{text} ", end="")

            print()

        print()