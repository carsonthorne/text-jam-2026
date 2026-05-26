from textual.app import App

from screens.main_menu import MainMenuScreen
from game_client import GameClient


class ChineseCheckersApp(App):

    BINDINGS = [
        ("ctrl+c", "quit", "Quit")
    ]

    def on_mount(self):

        self.client = GameClient()
        self.push_screen(MainMenuScreen())

if __name__ == "__main__":
    app = ChineseCheckersApp()
    app.run()