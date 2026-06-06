from textual.screen import Screen
from textual.app import ComposeResult
from textual.widgets import Button, Static, Input
from textual.containers import Vertical

from chinese_checkers.client.local_identity import save_identity
from chinese_checkers.ui.screens.lobby_screen import LobbyScreen
from chinese_checkers.shared.settings import PUBLIC_SERVER_HOST, SERVER_PORT
from chinese_checkers.shared.message_types import (
    SESSION_VALIDATED,
    INVALID_SESSION
)

class JoinSessionScreen(Screen):

    def __init__(self):
        super().__init__()

        self.message_handlers = {
            SESSION_VALIDATED: self._handle_session_validated,
            INVALID_SESSION: self._handle_invalid_session
        }


    def compose(self) -> ComposeResult:

        self.session_id_input = Input(placeholder="Enter session ID", id="session_id")

        yield Vertical(
            Static("[bold cyan]Join Session[/]"),
            self.session_id_input,
            Button("Join Session", id="join_session"),
            Button("Back to Main Menu", id="back")
        )


    def on_mount(self):

        self.app.client.on_message = self.handle_message

        self.session_id_input.focus()

    def handle_message(self, data):

        handler = self.message_handlers.get(
            data["type"]
        )

        if handler:
            handler(data)


    def _handle_session_validated(self, data):

        self.app.call_from_thread(
            self.app.push_screen,
            LobbyScreen(
                self.app.client,
                self.app.client.identity
            )
        )


    def _handle_invalid_session(self, data):

        identity = self.app.client.identity

        identity["session_id"] = None

        save_identity(identity)

        self.app.call_from_thread(
            self.notify,
            "Session ID does not exist.",
            severity="error"
        )


    def on_button_pressed(self, event: Button.Pressed):

        if event.button.id == "join_session":
            
            session_input = self.query_one(
                "#session_id",
                Input
            )

            session_id = session_input.value.strip().upper()

            if not session_id:
                return
            
            client = self.app.client

            identity = client.identity

            try:

                client.connect_to_session(
                    PUBLIC_SERVER_HOST,
                    SERVER_PORT,
                    identity,
                    session_id=session_id
                )

            except ConnectionRefusedError:

                self.notify(
                    "Cannot connect to server.",
                    severity="error"
                )

                return

        elif event.button.id == "back":

            self.app.pop_screen()


