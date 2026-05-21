import math
from rich.text import Text
from rich.style import Style

from board_definition import (
    ROWS,
    SPACING,
    COORD_TO_ZONE,
    HOME_COLORS,
    CURSOR_PULSE_GREYS,
    ZONE_BG_COLORS
)

class BoardRenderer:

    def build_board_text(
        self,
        board,
        player_configs,
        cursor=None,
        selected_path=None,
        tick=0
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
        SELECTED_STYLE = Style(bgcolor="grey50")
        
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

                # Cursor pulse highlight
                if coord == cursor:

                    phase = (math.sin(tick * 0.25) + 1) / 2

                    index = int(phase * (len(CURSOR_PULSE_GREYS) - 1))
                    pulse_color = CURSOR_PULSE_GREYS[index]

                    overlay_style = Style(bgcolor=pulse_color, bold=True)

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