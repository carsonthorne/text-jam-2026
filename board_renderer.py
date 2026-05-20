from rich.text import Text
from rich.style import Style

from board_definition import (
    ROWS,
    SPACING,
    COORD_TO_ZONE,
    HOME_COLORS,
)

class BoardRenderer:

    def build_board_text(
        self,
        board,
        player_configs,
        cursor=None,
        selected_path=None
    ):

        PLAYER_STYLES = {}

        for config in player_configs:

            player_number = config["player"]

            goal_zone = config["goal"]

            PLAYER_STYLES[player_number] = Style(
                color=HOME_COLORS[goal_zone],
                bold=True
            )
        
        EMPTY_STYLE = Style(color="white")
        HOME_EMPTY_STYLE = Style(color="black")

        CURSOR_STYLE = Style(bgcolor="grey50", bold=True)
        SELECTED_STYLE = Style(bgcolor="grey50")
        
        if selected_path is None:
            selected_path = []

        lines = []

        for row, tiles in ROWS.items():

            line = Text(" " * SPACING[row])

            for label, coord in tiles:

                occupant = board.get(coord)

                home_zone = COORD_TO_ZONE.get(coord)
                bg_color = HOME_COLORS.get(home_zone)

                cell_style = Style(bgcolor=bg_color) if bg_color else Style()

                # Cursor highlight
                if coord == cursor:
                    cell_style += CURSOR_STYLE

                # Selected path highlight
                if coord in selected_path:
                    cell_style += SELECTED_STYLE

                if occupant is None:
                    if coord == cursor:
                        style = HOME_EMPTY_STYLE
                    else:
                        style = EMPTY_STYLE

                    cell = Text("○", style=cell_style + style)

                elif occupant is not None:

                    piece_style = PLAYER_STYLES.get(occupant)

                    cell = Text(
                        "●", style=cell_style + piece_style
                    )
                
                line.append(cell)
                line.append(" ")

            lines.append(line)

        output = Text()
        for i, line in enumerate(lines):
            output.append(line)
            if i != len(lines) - 1:
                output.append("\n")

        return output