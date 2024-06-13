import logging
from watchdog.events import FileSystemEventHandler

class FileMonitorHandler(FileSystemEventHandler):
    def on_any_event(self, event):
        print(event)
    
    def on_moved(self, event) -> None:
        print(event)

    def on_created(self, event) -> None:
        logging.info(f"new file created: {event.src_path}")

    def on_deleted(self, event) -> None:
        print(event)

    def on_modified(self, event):
        print(event)