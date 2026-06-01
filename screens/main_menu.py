from textual.screen import Screen
from textual.app import ComposeResult
from textual.widgets import Button, Static
from textual.containers import Vertical

from screens.game_screen import GameScreen
from screens.lobby_screen import LobbyScreen
from screens.identity_screen import IdentityScreen
from screens.join_session_screen import JoinSessionScreen
from local_identity import save_identity, load_identity, clear_identity
from message_types import ERROR, SESSION_VALIDATED, INVALID_SESSION, DUPLICATE_PLAYER
from config import SERVER_HOST, SERVER_PORT

class MainMenuScreen(Screen):

    def __init__(self):
        super().__init__()

        self.app.client.on_message = self.handle_message

        self.message_handlers = {
            SESSION_VALIDATED: self._handle_session_validated,
            INVALID_SESSION: self._handle_invalid_session,
            DUPLICATE_PLAYER: self._handle_duplicate_player
        }


    def compose(self) -> ComposeResult:

        yield Vertical(
            Static("[bold cyan]Chinese Checkers[/]"),

            Button("Create Session", id="create"),
            Button("Join Session", id="join"),
            Button("Rules", id="rules"),
            Button("Controls", id="controls"),
            Button("Switch Player", id="switch_player"),
            Button("Quit", id="quit")
        )


    def on_mount(self):
        self.app.client.on_message = self.handle_message

        identity = load_identity()

        if identity:
            self.app.client.identity = identity

            if identity["session_id"] is not None:

                try:

                    self.app.client.connect_to_session(
                        SERVER_HOST,
                        SERVER_PORT,
                        identity,
                        session_id=identity["session_id"],
                    )

                except Exception:

                    pass
        else:

            self.app.push_screen(IdentityScreen())


    def handle_message(self, data):
        if data["type"] == ERROR:
            print(data["message"])

        handler = self.message_handlers.get(data["type"])

        if handler:
            handler(data)


    def _handle_duplicate_player(self, data):

        clear_identity()

        self.app.call_from_thread(self.app.push_screen, IdentityScreen())


    def _handle_invalid_session(self, data):
        identity = self.app.client.identity
        identity["session_id"] = None
        save_identity(identity)


    def _handle_session_validated(self, data):
        state = data["session_state"]

        player_num = data["player_num"]
        player_configs = data["player_configs"]

        if state == "lobby":
            self.app.call_from_thread(
                self.app.push_screen,
                LobbyScreen(self.app.client, self.app.client.identity)
            )

        elif state == "in_progress":
            self.app.call_from_thread(
                self.app.push_screen,
                GameScreen(
                    self.app.client,
                    self.app.client.identity,
                    player_num,
                    player_configs
                )
            )


    def on_button_pressed(self, event: Button.Pressed):

        button_id = event.button.id

        if button_id == "quit":

            self.app.exit()

        elif button_id == "create":

            self.create_session(2)
        
        elif button_id == "join":

            identity = self.app.client.identity

            if not identity:
                self.app.push_screen(IdentityScreen())
                return

            self.app.push_screen(JoinSessionScreen())

        elif button_id == "switch_player":

            clear_identity()

            self.app.client.identity = None

            self.app.push_screen(IdentityScreen())


    def create_session(self, num_players):

        client = self.app.client
        identity = client.identity

        if not identity:
            self.app.push_screen(IdentityScreen())
            return

        client.connect_to_session(
            SERVER_HOST,
            SERVER_PORT,
            identity,
            session_id=None,
            num_players=num_players
        )

        self.app.push_screen(
            LobbyScreen(client, identity)
        )