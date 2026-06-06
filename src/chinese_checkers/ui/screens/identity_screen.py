from textual.screen import Screen
from textual.app import ComposeResult
from textual.widgets import Input, Button, Static
from textual.containers import Vertical

import uuid

from chinese_checkers.client.local_identity import save_identity

class IdentityScreen(Screen):

    def compose(self) -> ComposeResult:

        self.name_input = Input(placeholder="Enter your name", id="name")

        yield Vertical(
            Static("[bold cyan]Create Identity[/]"),
            self.name_input,
            Button("Continue", id="continue")
        )


    def on_mount(self):

        self.name_input.focus()


    def on_button_pressed(self, event: Button.Pressed):

        if event.button.id != "continue":
            return
        
        name_input = self.query_one("#name", Input)

        entered_name = name_input.value.strip()

        if not entered_name:
            return

        identity = {
            "player_id": str(uuid.uuid4()),
            "session_id": None,
            "name": entered_name
        }

        save_identity(identity)

        self.app.client.identity = identity

        self.app.pop_screen()