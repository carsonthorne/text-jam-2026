from textual.app import App, ComposeResult
from textual.widgets import Static, RichLog
from textual.containers import Horizontal
from textual.events import Key

import socket
import threading
import sys

from local_identity import load_identity, save_identity
from board_renderer import BoardRenderer
from board_layout import ZONE_CURSOR_STARTS
from geometry import DIRECTIONS
from local_identity import load_identity
from network import send_json, receive_json
from screens.main_menu import MainMenuScreen
from screens.game_screen import GameScreen


class ChineseCheckersApp(App):

    BINDINGS = [
        ("ctrl+c", "quit", "Quit")
    ]

    def on_mount(self):

        self.push_screen(
            MainMenuScreen()
        )

if __name__ == "__main__":
    app = ChineseCheckersApp()
    app.run()