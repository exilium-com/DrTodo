"""Typer Aliases is a Typer wrapper to add arbitrary aliases to Typer commands with one line of code."""
__version__ = "1.0.0"
from .core import TyperAliases
from .core import TyperAliases as Typer
__all__ = ["Typer", "TyperAliases"]
