"""
Event system for ImagePass
Provides event-driven communication between components
"""

import threading
from typing import Dict, List, Callable, Any
from .interfaces import IEventManager


class Event:
    """Event data structure"""
    
    def __init__(self, event_type: str, data: Any = None, source: str = None):
        self.type = event_type
        self.data = data
        self.source = source
        self.timestamp = threading.get_ident()


class EventBus(IEventManager):
    """Event bus implementation"""
    
    def __init__(self):
        self._subscribers: Dict[str, List[Callable]] = {}
        self._lock = threading.RLock()
    
    def subscribe(self, event_type: str, handler: Callable):
        """Subscribe to event"""
        with self._lock:
            if event_type not in self._subscribers:
                self._subscribers[event_type] = []
            
            if handler not in self._subscribers[event_type]:
                self._subscribers[event_type].append(handler)
    
    def unsubscribe(self, event_type: str, handler: Callable):
        """Unsubscribe from event"""
        with self._lock:
            if event_type in self._subscribers:
                try:
                    self._subscribers[event_type].remove(handler)
                    if not self._subscribers[event_type]:
                        del self._subscribers[event_type]
                except ValueError:
                    pass  # Handler not found
    
    def publish(self, event_type: str, data: Any = None):
        """Publish event"""
        event = Event(event_type, data)
        
        with self._lock:
            subscribers = self._subscribers.get(event_type, []).copy()
        
        # Execute handlers outside of lock
        for handler in subscribers:
            try:
                handler(event)
            except Exception as e:
                print(f"Error in event handler for {event_type}: {e}")
    
    def get_subscribers_count(self, event_type: str) -> int:
        """Get number of subscribers for event type"""
        with self._lock:
            return len(self._subscribers.get(event_type, []))
    
    def clear_all(self):
        """Clear all subscriptions"""
        with self._lock:
            self._subscribers.clear()


# Event types
class EventTypes:
    """Standard event types"""
    # File events
    FILE_SELECTED = "file_selected"
    DIRECTORY_SELECTED = "directory_selected"
    FILES_LOADED = "files_loaded"
    
    # Processing events
    PROCESSING_STARTED = "processing_started"
    PROCESSING_PROGRESS = "processing_progress"
    PROCESSING_COMPLETE = "processing_complete"
    PROCESSING_ERROR = "processing_error"
    PROCESSING_STOPPED = "processing_stopped"
    
    # UI events
    UI_STATE_CHANGED = "ui_state_changed"
    PREVIEW_UPDATED = "preview_updated"
    CONFIG_CHANGED = "config_changed"
    
    # Navigation events
    NAVIGATION_NEXT = "navigation_next"
    NAVIGATION_PREVIOUS = "navigation_previous"
    NAVIGATION_CHANGED = "navigation_changed"


# Decorator for event subscription
def subscribe_to(event_type: str):
    """Decorator for event subscription"""
    def decorator(func):
        def wrapper(self, *args, **kwargs):
            if hasattr(self, '_event_bus') and self._event_bus:
                self._event_bus.subscribe(event_type, lambda e: func(self, e))
            return func
        return wrapper
    return decorator