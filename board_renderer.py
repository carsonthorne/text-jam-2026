from board_definition import (
    ROWS,
    SPACING,
    HOME_POSITIONS,
    LABEL_TO_HOME_COLOR,
    COORD_TO_LABEL,
    HOME_COLORS)

class BoardRenderer:

    def build_board_string(
        self,
        board,
        cursor=None,
        selected_path=None
    ):

        if selected_path is None:
            selected_path = []

        BLUE = "\033[94m"
        RED = "\033[91m"
        RESET = "\033[0m"

        CURSOR = "\033[7m"

        lines = []

        for row, tiles in ROWS.items():

            line = " " * SPACING[row]

            for label, coord in tiles:

                occupant = board.get(coord)

                home_zone = LABEL_TO_HOME_COLOR.get(label)
                bg = HOME_COLORS.get(home_zone, "")

                style = bg

                if coord == cursor:
                    style += CURSOR

                if coord in selected_path:
                    style += "\033[95m"

                if occupant is None:
                    text = f"{style}○{RESET}"

                elif occupant == 1:
                    text = f"{style}{BLUE}●{RESET}"

                elif occupant == 2:
                    text = f"{style}{RED}●{RESET}"

                else:
                    text = f"{style}??{RESET}"

                line += f"{text} "

            lines.append(line)

        return "\n".join(lines)