from rich.console import Console
from rich.theme import Theme

custom_theme = Theme({
    "index": "bright_black",
    "hash": "italic dim yellow",
    "text": "white",
    "header": "bold cyan",
    "warning": "bold yellow",
    "error": "red",
})
console = Console(theme=custom_theme)
