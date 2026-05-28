from textual.screen import Screen
from textual.app import ComposeResult
from textual.widgets import Button, Static, Input
from textual.containers import Vertical

from screens.lobby_screen import LobbyScreen

HOST = "127.0.0.1"
PORT = 5555

class JoinSessionScreen(Screen):


    def compose(self) -> ComposeResult:

        yield Vertical(
            Static("[bold cyan]Join Session[/]"),
            Input(placeholder="Enter session ID", id="session_id"),
            Button("Join Session", id="join_session")
        )


    def on_button_pressed(self, event: Button.Pressed):

        if event.button.id != "join_session":
            return
        
        session_input = self.query_one(
            "#session_id",
            Input
        )

        session_id = session_input.value.strip()

        if not session_id:
            return
        
        client = self.app.client

        identity = client.identity

        client.connect(HOST, PORT)

        self.app.push_screen(
            LobbyScreen(client, identity)
        )

        client.send({
            "type": "connect",
            "player_id": identity["player_id"],
            "session_id": session_id,
            "name": identity["name"]
        })