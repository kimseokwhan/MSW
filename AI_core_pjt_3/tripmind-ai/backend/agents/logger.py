from backend.database.store import append_event


def record_event(event):
    append_event(event)
