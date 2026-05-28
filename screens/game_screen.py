from textual.screen import Screen
from textual.app import ComposeResult
from textual.widgets import Static, RichLog
from textual.containers import Horizontal
from textual.events import Key

from board_renderer import BoardRenderer
from board_layout import ZONE_CURSOR_STARTS
from geometry import DIRECTIONS
from message_types import WAITING_FOR_PLAYERS, GAME_STATE, VALIDATE_PARTIAL, PARTIAL_VALIDATION, MOVE, ERROR, RECONNECTED


class GameScreen(Screen):

    def __init__(self, client, identity, player_number, player_configs):
        
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

        player_config = next(
            (
                config
                    for config in self.player_configs
                    if config["player"] == self.player_number
            ),
            None
        )

        if player_config is None:
            self.log_message("[red]Failed to load player config[/]")
            return

        start_zone = player_config["start"]

        self.cursor = ZONE_CURSOR_STARTS[start_zone]


    def animate_cursor(self):

        self.tick += 1

        self.refresh_board()


    def handle_message(self, data):

        msg_type = data["type"]

        if msg_type == WAITING_FOR_PLAYERS:

            self.client.dispatch_to_ui(
                self.app,
                self.log_message,
                "[yellow]Waiting for more players...[/]"
            )

        elif msg_type == RECONNECTED:

            self.client.dispatch_to_ui(
                self.app,
                self.log_message,
                "[green]Reconnected to game.[/]"
            )

        elif msg_type == PARTIAL_VALIDATION:

            self.client.dispatch_to_ui(
                self.app,
                self.handle_partial_validation,
                data["valid"],
                data["message"],
                self.cursor
            )

        elif msg_type == GAME_STATE:

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

        elif msg_type == ERROR:

            self.client.dispatch_to_ui(
                self.app,
                self.show_error,
                data["message"]
            )


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

        elif not self.my_turn and was_my_turn:

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
