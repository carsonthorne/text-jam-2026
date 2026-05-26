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
    
    def cleanup_sessions(self):

        abandoned = []

        for session_id, session in self.sessions.items():

            if session.is_abandoned():

                abandoned.append(session_id)

        for session_id in abandoned:

            print(f"Cleaning up session {session_id}")

            del self.sessions[session_id]