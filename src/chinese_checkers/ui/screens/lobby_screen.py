from textual.screen import Screen
from textual.app import ComposeResult
from textual.widgets import Static, Button, Select, RichLog
from textual.containers import Vertical

from chinese_checkers.client.local_identity import save_identity
from chinese_checkers.ui.screens.game_screen import GameScreen
from chinese_checkers.shared.message_types import (
    WELCOME,
    LOBBY_STATE,
    GAME_STARTED,
    START_GAME,
    UPDATE_NUM_PLAYERS,
    LEAVE_LOBBY
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
        self.client.on_disconnect = self.handle_disconnect
        self.client.log_message = self.log_message


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
        self.back_button = Button("Leave Lobby", id="leave_lobby")

        self.message_log = RichLog(
            highlight=True,
            markup=True,
            wrap=True
        )

        yield Vertical(
            self.title_widget,
            self.player_count_select,
            self.players_widget,
            self.status_widget,
            self.start_button,
            self.back_button,
            self.message_log

        )


    def on_mount(self):

        # self.refresh_lobby()
        if self.session_id and self.players:
            self.refresh_lobby()


    def log_message(self, message):

            self.message_log.write(message)


    def refresh_lobby(self):

        self.title_widget.update(
            f"[bold cyan]Lobby[/]\nSession ID: {self.session_id}"
        )

        if self.num_players is not None:
            self.player_count_select.value = self.num_players

        player_lines = []

        # Update player list
        for player in self.players:

            name = player["name"]

            if player["is_host"]:
                name += "[grey] (host)[/]"

            status = (
                "[green](connected)[/]"
                if player["connected"]
                else "[red](disconnected)[/]"
            )

            player_lines.append(f"{name} {status}")

        self.players_widget.update(
            "\n".join(player_lines)
        )

        # Update status
        connected_players = sum(
            1 for player in self.players
            if player["connected"]
        )

        all_connected = all(
            player["connected"]
            for player in self.players
        )

        if (connected_players == self.num_players and all_connected):
            if self.is_host:
                status_message = "[bold green]Ready to start game[/]"
            else:
                status_message = "[bold green]Waiting for host to start game[/]"
        elif (connected_players < self.num_players or not all_connected):
            status_message = "[bold yellow]Waiting for players...[/]"
        elif connected_players > self.num_players:
            status_message = "[bold red]Too many players...[/]"
        self.status_widget.update(
            status_message
        )

        # Update dropdown if player has become the new host
        if self.is_host and self.player_count_select.disabled:
            self.player_count_select.disabled = False

        # Update start button
        can_start = (
            self.is_host
            and connected_players == self.num_players
            and all_connected
        )

        self.start_button.disabled = not can_start


    def handle_disconnect(self):

        self.status_widget.update("[bold red]Connection to server lost.[/]")


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

        if event.button.id == "leave_lobby":

            self.client.send({
                "type": LEAVE_LOBBY
            })

            self.identity["session_id"] = None

            save_identity(self.identity)

            self.client.close()

            self.app.pop_screen()


    def on_select_changed(self, event: Select.Changed):

        if event.select.id == "player_count":

            if event.value is Select.NULL:
                return

            self.client.send({
                "type": UPDATE_NUM_PLAYERS,
                "num_players": event.value
            })