from message_types import (
    GAME_STATE,
    ERROR,
    WELCOME,
    LOBBY_STATE,
    PARTIAL_VALIDATION,
    GAME_STARTED,
    RECONNECTED,
    SESSION_VALIDATED,
    INVALID_SESSION,
    DUPLICATE_PLAYER
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


def make_partial_validation(valid, message):

    return {
        "type": PARTIAL_VALIDATION,
        "valid": valid,
        "message": message
    }


def make_game_started():

    return {
        "type": GAME_STARTED
    }


def make_reconnected():

    return {
        "type": RECONNECTED
    }


def make_invalid_session():

    return {
        "type": INVALID_SESSION
    }


def make_session_validated(session, player_num):

    return {
        "type": SESSION_VALIDATED,
        "session_state": session.state,
        "num_players": session.num_players,
        "player_num": player_num,
        "player_configs": session.game_state.players
    }


def make_duplicate_player():

    return {
        "type": DUPLICATE_PLAYER
    }