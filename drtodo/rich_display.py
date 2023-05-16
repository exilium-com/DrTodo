from rich.console import Console
from rich.theme import Theme
from .settings import settings

# TODO: https://github.com/exilium-com/DrTodo/issues/1 - make this configurable

_console = None


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
