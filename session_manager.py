import uuid
import threading

from session import Session

class SessionManager:

    def __init__(self):
        
        self.sessions = {}
        self.lock = threading.Lock()


    def create_session(self, num_players):

        session_id = str(uuid.uuid4())

        session = Session(
            session_id=session_id,
            num_players=num_players
        )

        with self.lock:

            self.sessions[session_id] = session

        return session
    
    
    def get_session(self, session_id):

        with self.lock:
            return self.sessions.get(session_id)

    
    def cleanup_sessions(self):

        abandoned = []

        with self.lock:

            sessions_copy = list(self.sessions.items())

            for session_id, session in sessions_copy:

                if session.is_abandoned():

                    abandoned.append(session_id)

        for session_id in abandoned:

            print(f"Cleaning up session {session_id}")

            with self.lock:

                del self.sessions[session_id]