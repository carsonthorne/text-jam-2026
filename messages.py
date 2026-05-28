from message_types import (
    GAME_STATE,
    ERROR,
    WELCOME,
    LOBBY_STATE
)

def make_error(message):

    return {
        "type": ERROR,
        "message": message
    }


def make_game_state(game_state):

    return {
        "type": GAME_STATE,
        "board": game_state.serialize_board(),
        "current_player": game_state.current_player_number,
        "winner": game_state.winner
    }


def make_welcome(player, session):

    return {
        "type": WELCOME,
        "player_number": player.player_number,
        "players": session.game_state.players,
        "session_id": session.session_id
    }


def make_lobby_state(session):

    return {
        "type": LOBBY_STATE,
        "players": session.serialize_players(),
        "session_id": session.session_id,
        "num_players": session.num_players
    }