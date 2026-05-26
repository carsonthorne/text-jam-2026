from session import Session
import uuid

class SessionManager:

    def __init__(self):
        
        self.sessions = {}

    def create_session(self, num_players):

        session_id = str(uuid.uuid4())

        session = Session(
            session_id=session_id,
            num_players=num_players
        )

        self.sessions[session_id] = session

        return session
    
    def get_session(self, session_id):

        return self.sessions.get(session_id)