from textual.screen import Screen
from textual.app import ComposeResult
from textual.widgets import Button, Static
from textual.containers import Vertical

from screens.game_screen import GameScreen
from screens.lobby_screen import LobbyScreen
from screens.identity_screen import IdentityScreen
from screens.join_session_screen import JoinSessionScreen
from local_identity import load_identity, clear_identity
from message_types import ERROR

HOST = "127.0.0.1"
PORT = 5555

class MainMenuScreen(Screen):

    def __init__(self):
        super().__init__()


    def compose(self) -> ComposeResult:

        yield Vertical(
            Static("[bold cyan]Chinese Checkers[/]"),

            # TODO change to dropdown menu instead of multiple buttons
            Button("Create 2 Player Session", id="create_2"),
            Button("Create 3 Player Session", id="create_3"),
            Button("Create 4 Player Session", id="create_4"),
            Button("Create 6 Player Session", id="create_6"),

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
        else:
            self.app.push_screen(IdentityScreen())


    def handle_message(self, data):
        if data["type"] == ERROR:
            print(data["message"])


    def on_button_pressed(self, event: Button.Pressed):

        button_id = event.button.id

        if button_id == "quit":

            self.app.exit()

        elif button_id.startswith("create_"):

            num_players = int(button_id.split("_")[1])

            self.create_session(num_players)
        
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
            HOST,
            PORT,
            identity,
            session_id=None,
            num_players=num_players
        )

        self.app.push_screen(
            LobbyScreen(client, identity)
        )