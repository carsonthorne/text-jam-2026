from textual.screen import Screen
from textual.app import ComposeResult
from textual.widgets import Static, RichLog
from textual.containers import Horizontal
from textual.events import Key
from rich.text import Text

from chinese_checkers.ui.board_renderer import BoardRenderer
from chinese_checkers.ui.board_layout import ZONE_CURSOR_STARTS
from chinese_checkers.ui.geometry import DIRECTIONS
from chinese_checkers.shared.message_types import (
    GAME_STATE,
    VALIDATE_PARTIAL,
    PARTIAL_VALIDATION,
    MOVE,
    ERROR,
    RECONNECTED,
    PLAYER_JOINED_GAME
)


class GameScreen(Screen):

    def __init__(self, client, identity, player_number=None, player_configs=None):
        
        super().__init__()

        self.client = client
        self.identity = identity

        self.renderer = BoardRenderer()

        self.board = {}

        self.player_number = player_number
        self.player_configs = player_configs

        self.my_turn = False
        self.selected_path = []

        self.cursor = None
        self.tick = 0

        self.client.on_message = self.handle_message
        self.client.on_disconnect = self.handle_disconnect
        self.client.log_message = self.log_message


        self.message_handlers = {
            GAME_STATE: self._handle_game_state,
            PARTIAL_VALIDATION: self._handle_partial_validation,
            ERROR: self._handle_error,
            RECONNECTED: self._handle_reconnect,
            PLAYER_JOINED_GAME: self._handle_player_joined_game
        }


    def compose(self) -> ComposeResult:

        self.board_widget = Static()

        self.message_log = RichLog(
            highlight=True,
            markup=True,
            wrap=True
        )

        self.board_widget.styles.width = "50%"
        self.message_log.styles.width = "50%"

        yield Horizontal(
            self.board_widget,
            self.message_log
        )


    def on_mount(self):

        self.refresh_board()

        self.set_interval(0.08, self.animate_cursor)

        if not self.player_configs:
            return

        player_config = next(
            (
                config
                for config in self.player_configs
                if config["player"] == self.player_number
            ),
            None
        )

        if player_config is None:
            return

        start_zone = player_config["start"]

        self.cursor = ZONE_CURSOR_STARTS[start_zone]


    def animate_cursor(self):

        self.tick += 1

        self.refresh_board()

    def handle_disconnect(self):

        # self.client.dispatch_to_ui(
        #     self.app,
        #     self.log_message,
        #     "[bold red]Connection to server lost...[/]"
        # )

        self.log_message("[bold red]Connection to server lost...[/]")

    def handle_message(self, data):

        handler = self.message_handlers.get(data["type"])

        if handler:
            handler(data)


    def _handle_game_state(self, data):

        serialized_board = data["board"]

        new_board = {}
        for key, value in serialized_board.items():
            q, r = map(int, key.split(","))
            new_board[(q, r)] = value

        self.client.dispatch_to_ui(
            self.app,
            self.update_game_state,
            new_board,
            data["current_player"],
            data.get("winner")
        )


    def _handle_partial_validation(self, data):
        
        self.client.dispatch_to_ui(
            self.app,
            self.handle_partial_validation,
            data["valid"],
            data["message"],
            self.cursor
        )
    
    
    def _handle_error(self, data):

        self.client.dispatch_to_ui(
            self.app,
            self.show_error,
            data["message"]
        )

    
    def _handle_reconnect(self, data):
    
        player_name = data["player_name"]

        self.client.dispatch_to_ui(
            self.app,
            self.log_message,
            f"[green]{player_name} reconnected to the game.[/]"
        )

    def _handle_player_joined_game(self, data):

        self.client.dispatch_to_ui(
            self.app,
            self.show_player_joined,
            data["player_name"],
            data["player_number"]
        )


    def show_player_joined(self, player_name, player_number):

        config = next(
            (
                config
                for config in self.player_configs
                if config["player"] == player_number
            ),
            None
        )

        if config is None:
            return

        message = Text(player_name, style=str(config["piece"]))
        message.append(" has joined the game!", style="white")
        self.message_log.write(message)


    def update_game_state(self, new_board, current_player, winner):

        self.board = new_board

        if not self.player_configs:
            return

        #-----------------
        # Handle game over
        #-----------------

        if winner is not None:

            self.my_turn = False

            if winner == self.player_number:

                self.log_message(
                    "[bold green]You win![/]"
                )

            else:

                self.log_message(
                    f"[bold red]Player {winner} wins.[/]"
                )

            self.refresh_board()

            return
        
        #------------
        # Normal turn
        #------------

        was_my_turn = self.my_turn

        self.my_turn = (
            current_player == self.player_number
        )

        if self.my_turn and not was_my_turn:
        
            self.log_message("[bold yellow]Your turn![/]")

        elif not self.my_turn:

            self.log_message("[cyan]Waiting for opponent...[/]")

        self.refresh_board()


    def show_error(self, message):

        self.log_message(f"[bold red]Invalid move:[/] {message}")


    def refresh_board(self):

        visible_cursor = (
            self.cursor if self.my_turn else None
        )

        board_text = self.renderer.build_board_text(
            self.board,
            self.player_configs,
            visible_cursor,
            self.selected_path,
            self.tick
        )

        self.board_widget.update(board_text)


    def cycle_to_next_piece(self):

        # Only allow cycling before selecting a piece
        if self.selected_path:
            return
        
        player_pieces = sorted(
            [
                coord
                for coord, occupant in self.board.items()
                if occupant == self.player_number
            ],
            key=lambda coord: (coord[1], coord[0])
        )

        if not player_pieces:
            return
        
        # If cursor isn't on one of the player's pieces,
        # jump to the first one
        if self.cursor not in player_pieces:

            self.cursor = player_pieces[0]

            self.refresh_board()

            return
        
        current_index = player_pieces.index(self.cursor)

        next_index = (
            current_index + 1
        ) % len(player_pieces)

        self.cursor = player_pieces[next_index]

        self.refresh_board()


    def on_key(self, event: Key):

        if not self.my_turn:
            return

        key = event.key.lower()

        if key in DIRECTIONS:

            direction = DIRECTIONS[key]

            new_coord = (
                self.cursor[0] + direction[0],
                self.cursor[1] + direction[1]
            )

            if new_coord in self.board:

                self.cursor = new_coord

                self.refresh_board()

        elif key == "tab":

            self.cycle_to_next_piece()

        elif key == "space":

            proposed_path = self.selected_path + [self.cursor]

            self.client.send({
                "type": VALIDATE_PARTIAL,
                "path": proposed_path
            })

        elif key == "enter":

            if len(self.selected_path) >= 2:

                self.send_move()

                self.selected_path.clear()

                self.refresh_board()

            elif len(self.selected_path) == 1:

                self.log_message("[bold red]Invalid move:[/] Select a tile to move to.")

            else:

                self.log_message("[bold red]Invalid move:[/] Select a piece to move.")

        elif key == "escape" and self.selected_path:

            self.cursor = self.selected_path[-1]

            self.selected_path.pop()

            self.refresh_board()


    def send_move(self):

        self.client.send({
            "type": MOVE,
            "path": self.selected_path
        })


    def handle_partial_validation(self, valid, message, coord):

        if valid:

            self.selected_path.append(coord)

            self.refresh_board()

        else:

            self.show_error(message)


    def log_message(self, message):

        self.message_log.write(message)
