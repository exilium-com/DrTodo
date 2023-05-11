from rich.console import Console
from rich.theme import Theme
import settings

# TODO: https://github.com/exilium-com/DrTodo/issues/1 - make this configurable

_console = None


def console():
    global _console
    if not _console:
        custom_theme = Theme({
            "index": settings.settings.style.index,
            "hash": settings.settings.style.hash,
            "text": settings.settings.style.text,
            "header": settings.settings.style.header,
            "warning": settings.settings.style.warning,
            "error": settings.settings.style.error,
        })
        _console = Console(theme=custom_theme)
    return _console
