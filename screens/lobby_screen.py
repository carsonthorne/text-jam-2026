from textual.screen import Screen
from textual.app import ComposeResult
from textual.widgets import Static
from textual.containers import Vertical

from local_identity import save_identity

class LobbyScreen(Screen):

    def __init__(self, client, identity):

        super().__init__()

        self.client = client
        self.identity = identity

        self.session_id = None

        self.client.on_message = self.handle_message

    def compose(self) -> ComposeResult:

        self.title_widget = Static()
        self.players_widget = Static()
        self.status_widget = Static()

        yield Vertical(
            self.title_widget,
            self.players_widget,
            self.status_widget
        )

    def on_mount(self):

        self.refresh_lobby()

    def refresh_lobby(self):

        self.title_widget.update(
            f"[bold cyan]Lobby[/]\nSession ID: {self.session_id}"
        )
        self.players_widget.update(
            f"Player name: {self.identity["name"]}"
        )

    def handle_message(self, data):

        msg_type = data["type"]

        if msg_type == "welcome":

            self.session_id = data["session_id"]

            self.identity["session_id"] = data["session_id"]

            save_identity(self.identity)

            self.player_number = data["player_number"]
            self.player_configs = data["players"]




            self.refresh_lobby()

        elif msg_type == "waiting_for_players":

            self.status_widget.update(
                "[yellow]Waiting for players...[/]"
            )

        elif msg_type == "game_started":

            from screens.game_screen import GameScreen

            self.app.push_screen(
                GameScreen(
                    self.client,
                    self.identity,
                    self.player_number,
                    self.player_configs
                )
            )