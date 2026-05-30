from textual.screen import Screen
from textual.app import ComposeResult
from textual.widgets import Static, Button, Select
from textual.containers import Vertical

from local_identity import save_identity
from screens.game_screen import GameScreen
from message_types import (
    WELCOME,
    LOBBY_STATE,
    GAME_STARTED,
    START_GAME,
    UPDATE_NUM_PLAYERS
)

class LobbyScreen(Screen):

    def __init__(self, client, identity):

        super().__init__()

        self.client = client
        self.identity = identity

        self.player_number = None
        self.is_host = False

        self.session_id = None
        self.players = []
        self.num_players = None
        self.player_configs = None

        self.client.on_message = self.handle_message

        self.message_handlers = {
            WELCOME: self._handle_welcome,
            GAME_STARTED: self._handle_game_started,
            LOBBY_STATE: self._handle_lobby_state
        }


    def compose(self) -> ComposeResult:

        self.title_widget = Static()
        self.player_count_select = Select(
            [
                ("2 Players", 2),
                ("3 Players", 3),
                ("4 Players", 4),
                ("6 Players", 6),
            ],
            value=2,
            prompt="Select number of players",
            id="player_count"
        )
        self.players_widget = Static()
        self.status_widget = Static()
        self.start_button = Button("Start Game", id="start_game")
        self.back_button = Button("Back to Main Menu", id="back")

        yield Vertical(
            self.title_widget,
            self.player_count_select,
            self.players_widget,
            self.status_widget,
            self.start_button,
            self.back_button
        )


    def on_mount(self):

        # self.refresh_lobby()
        if self.session_id and self.players:
            self.refresh_lobby()


    def refresh_lobby(self):

        self.title_widget.update(
            f"[bold cyan]Lobby[/]\nSession ID: {self.session_id}"
        )

        if self.num_players is not None:
            self.player_count_select.value = self.num_players

        player_lines = []

        # Update player list
        for player in self.players:

            status = (
                "[green](connected)[/]"
                if player["connected"]
                else "[red](disconnected)[/]"
            )

            player_lines.append(
                f"Player {player['player_number']}: "
                f"{player['name']} {status}"
            )

        self.players_widget.update(
            "\n".join(player_lines)
        )

        # Update status
        if len(self.players) == self.num_players:
            if self.is_host:
                status_message = "[bold green]Ready to start game[/]"
            else:
                status_message = "[bold green]Waiting for host to start game[/]"
        elif len(self.players) < self.num_players:
            status_message = "[bold yellow]Waiting for players...[/]"
        elif len(self.players) > self.num_players:
            status_message = "[bold red]Too many players...[/]"
        self.status_widget.update(
            status_message
        )

    def handle_message(self, data):

        handler = self.message_handlers.get(data["type"])

        if handler:
            handler(data)


    def _handle_welcome(self, data):

        self.session_id = data["session_id"]

        self.identity["session_id"] = data["session_id"]

        save_identity(self.identity)

        self.player_number = data["player_number"]

        # Only host can start the game
        if not self.is_host:
            self.start_button.disabled = True
            self.player_count_select.disabled = True

        self.player_configs = data["players"]

        self.client.dispatch_to_ui(
            self.app,
            self.refresh_lobby
        )


    def _handle_game_started(self, data):

        self.player_number = data["player_number"]

        self.player_configs = data["player_configs"]

        self.client.dispatch_to_ui(
            self.app,
            self._enter_game_screen
        )


    def _handle_lobby_state(self, data):

        self.session_id = data["session_id"]

        self.players = data["players"]

        self.num_players = data["num_players"]

        self.is_host = data["is_host"]

        self.client.dispatch_to_ui(
            self.app,
            self.refresh_lobby
        )


    def _enter_game_screen(self):
        
        self.client.send({"type": "debug", "message": f"Lobby Screen: _enter_game_screen: {self.player_number}"})

        self.app.push_screen(
            GameScreen(
                self.client,
                self.identity,
                self.player_number,
                self.player_configs
            )
        )


    def on_button_pressed(self, event):

        if event.button.id == "start_game":

            self.client.send({
                "type": START_GAME
            })

        if event.button.id == "back":

            self.app.pop_screen()


    def on_select_changed(self, event: Select.Changed):

        if event.select.id == "player_count":

            if event.value is Select.NULL:
                return

            self.client.send({
                "type": UPDATE_NUM_PLAYERS,
                "num_players": event.value
            })