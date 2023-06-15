from rich.console import Console
from rich.theme import Theme
from .settings import settings

_console = None
_error_console = None

def console():
    global _console
    if not _console:
        custom_theme = Theme({
            "index": settings.style.index,
            "hash": settings.style.hash,
            "text": settings.style.text,
            "header": settings.style.header,
            "warning": settings.style.warning,
            "error": settings.style.error,
        })
        _console = Console(theme=custom_theme)
    return _console


def error_console():
    global _error_console
    if not _error_console:
        _error_console = Console(stderr=True, style="red")
    return _error_console
