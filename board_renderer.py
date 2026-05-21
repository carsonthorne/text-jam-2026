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

        ZONE_BG_COLORS = {
            "red1": "red3",
            "white": "bright_black",
            "purple4": "blue_violet",
            "spring_green3": "spring_green4",
            "dodger_blue2": "dark_blue",
            "dark_orange": "orange_red1",
        }
        
        if selected_path is None:
            selected_path = []

        lines = []

        for row, tiles in ROWS.items():

            line = Text(" " * SPACING[row])

            for label, coord in tiles:

                occupant = board.get(coord)

                background_style = Style()
                overlay_style = Style()
                foreground_style = Style()

                home_zone = COORD_TO_ZONE.get(coord)

                if home_zone:
                    zone_color = HOME_COLORS[home_zone]
                    bg_color = ZONE_BG_COLORS[zone_color]
                    background_style = Style(bgcolor=bg_color)

                # Cursor highlight
                if coord == cursor:
                    overlay_style += CURSOR_STYLE

                # Selected path highlight
                if coord in selected_path:
                    overlay_style += SELECTED_STYLE

                if occupant is None:
                    
                    foreground_style = EMPTY_STYLE
                    char = "○"

                elif occupant is not None:

                    foreground_style = PLAYER_STYLES.get(occupant, Style())
                    char = "●"
                
                final_style = background_style + overlay_style + foreground_style
                cell = Text(char, style=final_style)

                line.append(cell)
                line.append(" ")

            lines.append(line)

        output = Text()
        for i, line in enumerate(lines):
            output.append(line)
            if i != len(lines) - 1:
                output.append("\n")

        return output