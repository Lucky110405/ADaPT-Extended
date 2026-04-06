from datetime import datetime

events = []

def log_event(type, message, data=None):
    events.append({
        "time": datetime.now().strftime("%H:%M:%S"),
        "type": type,
        "message": message,
        "data": data
    })

def get_events():
    return events

def clear_events():
    global events
    events = []