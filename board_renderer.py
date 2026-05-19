from rich.text import Text
from rich.style import Style

from board_definition import (
    ROWS,
    SPACING,
    HOME_POSITIONS,
    LABEL_TO_HOME_COLOR,
    COORD_TO_LABEL,
    HOME_COLORS)

class BoardRenderer:

    def build_board_text(
        self,
        board,
        cursor=None,
        selected_path=None
    ):

        if selected_path is None:
            selected_path = []

        lines = []

        GREEN_STYLE = Style(color="spring_green3", bold=True)
        RED_STYLE = Style(color="red1", bold=True)
        EMPTY_STYLE = Style(color="white")

        CURSOR_STYLE = Style(bgcolor="grey50", bold=True)
        SELECTED_STYLE = Style(bgcolor="grey50")

        for row, tiles in ROWS.items():

            line = Text(" " * SPACING[row])

            for label, coord in tiles:

                occupant = board.get(coord)

                home_zone = LABEL_TO_HOME_COLOR.get(label)
                bg_color = HOME_COLORS.get(home_zone)

                cell_style = Style(bgcolor=bg_color) if bg_color else Style()

                # Cursor highlight
                if coord == cursor:
                    cell_style += CURSOR_STYLE

                # Selected path highlight
                if coord in selected_path:
                    cell_style += SELECTED_STYLE

                if occupant is None:
                    cell = Text("○", style=cell_style + EMPTY_STYLE)

                elif occupant == 1:
                    cell = Text("●", style=cell_style + GREEN_STYLE)

                elif occupant == 2:
                    cell = Text("●", style=cell_style + RED_STYLE)

                else:
                    cell = Text("??", style=cell_style)

                line.append(cell)
                line.append(" ")

            lines.append(line)

        output = Text()
        for i, line in enumerate(lines):
            output.append(line)
            if i != len(lines) - 1:
                output.append("\n")

        return output