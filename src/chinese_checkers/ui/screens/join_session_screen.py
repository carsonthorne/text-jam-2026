from textual.screen import Screen
from textual.app import ComposeResult
from textual.widgets import Button, Static, Input
from textual.containers import Vertical

from chinese_checkers.ui.screens.lobby_screen import LobbyScreen
from chinese_checkers.shared.settings import SERVER_HOST, SERVER_PORT

class JoinSessionScreen(Screen):

    def compose(self) -> ComposeResult:

        yield Vertical(
            Static("[bold cyan]Join Session[/]"),
            Input(placeholder="Enter session ID", id="session_id"),
            Button("Join Session", id="join_session"),
            Button("Back to Main Menu", id="back")
        )


    def on_button_pressed(self, event: Button.Pressed):

        if event.button.id == "join_session":
            
            session_input = self.query_one(
                "#session_id",
                Input
            )

            session_id = session_input.value.strip()

            if not session_id:
                return
            
            client = self.app.client

            identity = client.identity

            client.connect_to_session(
                SERVER_HOST,
                SERVER_PORT,
                identity,
                session_id=session_id
            )

            self.app.push_screen(
                LobbyScreen(client, identity)
            )

        elif event.button.id == "back":

            self.app.pop_screen()


