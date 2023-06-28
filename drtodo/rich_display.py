from rich.console import Console
from rich.theme import Theme

_console = None
_error_console = None

def console():
    from . import config

    global _console
    if not _console:
        custom_theme = Theme({
            "index": config.settings.style.index,
            "hash": config.settings.style.hash,
            "text": config.settings.style.text,
            "header": config.settings.style.header,
            "warning": config.settings.style.warning,
            "error": config.settings.style.error,
        })
        _console = Console(theme=custom_theme)
    return _console


def error_console():
    global _error_console
    if not _error_console:
        _error_console = Console(stderr=True, style="red")
    return _error_console
