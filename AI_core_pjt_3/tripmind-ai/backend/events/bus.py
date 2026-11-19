import logging
from uuid import uuid4

from backend.database.store import utc_now


class EventBus:
    def __init__(self, session_id, run_id, subscribers=()):
        self.session_id = session_id
        self.run_id = run_id
        self.subscribers = subscribers
        self.events = []

    def publish(self, event_type, node, **payload):
        event = dict(event_id=str(uuid4()), session_id=self.session_id, run_id=self.run_id,
                     seq=len(self.events) + 1, type=event_type, node=node,
                     occurred_at=utc_now(), payload=payload)
        self.events.append(event)
        for subscriber in self.subscribers:
            try:
                subscriber(event)
            except Exception:
                logging.getLogger(__name__).warning("Execution log subscriber failed")
