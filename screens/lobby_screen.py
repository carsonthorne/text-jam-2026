from textual.screen import Screen
from textual.app import ComposeResult
from textual.widgets import Static, Button
from textual.containers import Vertical

from local_identity import save_identity
from screens.game_screen import GameScreen

class LobbyScreen(Screen):

    def __init__(self, client, identity):

        super().__init__()

        self.client = client
        self.identity = identity

        self.session_id = None
        self.players = []
        self.num_players = None

        self.client.on_message = self.handle_message


    def compose(self) -> ComposeResult:

        self.title_widget = Static()
        self.players_widget = Static()
        self.status_widget = Static()
        self.start_button = Button("Start Game", id="start_game")

        yield Vertical(
            self.title_widget,
            self.players_widget,
            self.status_widget,
            self.start_button
        )


    def on_mount(self):

        self.refresh_lobby()


    def refresh_lobby(self):

        self.title_widget.update(
            f"[bold cyan]Lobby[/]\nSession ID: {self.session_id}"
        )

        player_lines = []

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


    def handle_message(self, data):

        msg_type = data["type"]

        if msg_type == "welcome":

            self.session_id = data["session_id"]

            self.identity["session_id"] = data["session_id"]

            save_identity(self.identity)

            self.player_number = data["player_number"]

            if self.player_number != 1:
                self.start_button.disabled = True

            self.player_configs = data["players"]

            self.app.call_from_thread(self.refresh_lobby)

        elif msg_type == "waiting_for_players":

            self.app.call_from_thread(
                self.status_widget.update,
                "[yellow]Waiting for players...[/]"
            )

        elif msg_type == "game_started":

            self.app.call_from_thread(self._enter_game_screen)

        elif msg_type == "lobby_state":

            self.session_id = data["session_id"]

            self.players = data["players"]

            self.num_players = data["num_players"]

            self.app.call_from_thread(self.refresh_lobby)


    def _enter_game_screen(self):
        
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
                "type": "start_game"
            })