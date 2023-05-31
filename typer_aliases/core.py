import inspect
from functools import wraps
from typing import Callable, Optional

import typer


class TyperAliases(typer.Typer):
    """
    Adds support for command aliases to typer apps. Just import this instead of typer, everything works as before,
    except that you can now use the `@app.command_alias()` decorator to add aliases to commands.
    Ex:
    ```python {4,6}
    import typer
    from typer_aliases import Typer  # import this instead or in addition to typer

    app = Typer()   # do not use typer.Typer()
    @app.command()
    @app.command_alias(name="ls")   # you can have as many of these as you want
    def list(folder: Path = typer.Argument(Path.cwd(), help="Folder to list")):
        ...
    ```

    If you need to customize how the help text for aliases is formatted, use the `@app.alias_format()` decorator
    on your app callback. Ex:
    ```python
    @app.alias_format(alias_help_formatter=lambda command_name: f"Alias of {command_name}",
                      aliases_help_formatter=lambda base_help, alias_list:
                        f"{base_help} aliases are {', '.join(alias_list)}")
    @app.callback()
    def main():
        ...
    ```
    """

    # simplest and cleanest way to add aliases is to derive from the Typer class, add a new method for the decorator,
    # and ovrride the __call__ method to initialize the command aliases after all commands are registered.

    def _init_typer_aliases(self, *,
                    alias_help_formatter: Optional[Callable[[str], str]] = None,
                    aliases_help_formatter: Optional[Callable[[str, list[str]], str]] = None) -> None:
        """
        Initializes typer aliases for all hidden commands and properly sets the help text for them.
        Parameters:
            app: the typer app to modify
            alias_help_formatter: formats a help string for an aliased command like f"Alias of {command name}"
            aliases_help_formatter: formats a help string for a command with aliases like f"Aliases: {alias1}, {alias2}"
        """

        def get_command_name(command_info) -> str:
            # borrowed from Typer.main.get_command_from_info()
            name = command_info.name or typer.main.get_command_name(command_info.callback.__name__)
            return name

        def get_command_help(command_info) -> Optional[str]:
            # borrowed from Typer.main.get_command_from_info()
            use_help = command_info.help
            if use_help is None:
                use_help = inspect.getdoc(command_info.callback)
            else:
                use_help = inspect.cleandoc(use_help)
            return use_help

        def format_alias_help(aliased_name: str) -> str:
            if self.rich_markup_mode == "markdown":
                return f"Alias of `{aliased_name}`"
            elif self.rich_markup_mode == "rich":
                return f"Alias of [bold]{aliased_name}[/bold]"
            else:
                return f"Alias of {aliased_name}"

        def format_aliases_help(base_help: str, aliases: list[str]) -> str:
            if self.rich_markup_mode == "markdown":
                return f"{base_help} *[or {', '.join([f'`{alias}`' for alias in aliases])}]*"
            elif self.rich_markup_mode == "rich":
                return f"{base_help} [italics][or {', '.join([f'[bold]{alias}[/bold]' for alias in aliases])}][/italics]"
            else:
                return f"{base_help} [or {', '.join(aliases)}]"

        alias_help_formatter = alias_help_formatter or format_alias_help
        aliases_help_formatter = aliases_help_formatter or format_aliases_help

        aliased_commands = set()
        # for each command that is not hidden, find any hidden command with the same callback
        for visible_command in [cmd for cmd in self.registered_commands if not cmd.hidden]:
            for hidden_command in [cmd for cmd in self.registered_commands if cmd.hidden]:
                if visible_command.callback == hidden_command.callback:
                    if not hidden_command.help:
                        hidden_command.help = alias_help_formatter(get_command_name(visible_command))
                    setattr(visible_command, 'aliases', getattr(visible_command, 'aliases', []) + [hidden_command])
                    aliased_commands.add(visible_command)

        # adjust help text for aliased commands
        for cmd in aliased_commands:
            basehelp = get_command_help(cmd)
            if basehelp:
                cmd.help =  aliases_help_formatter(basehelp, [get_command_name(alias) for alias in cmd.aliases])

    # using decorator syntax ensures these methods are only done at app initialization time
    def alias_format(self,
                     alias_help_formatter: Optional[Callable[[str], str]] = None,
                     aliases_help_formatter: Optional[Callable[[str, list[str]], str]] = None):
        """
        Use as decorator on a typer app to customize how help text for aliases is formatted.
        Parameters:
            alias_help_formatter(command_name): formats a help string for an aliased
                command. Ex: `return f"This is an alias of {command_name}"`
            aliases_help_formatter(base_help, alias_list): formats a help string for a command with aliases
                Ex: `return f"{base} aliases are {', '.join(alias_list)}"
        """
        self.alias_help_formatter=alias_help_formatter
        self.aliases_help_formatter=aliases_help_formatter

        def identity (func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                return func(*args, **kwargs)
            return wrapper
        return identity


    def command_alias(self, name: str, *args, **kwargs):
        """
        Use as decorator on a typer command to add aliases for this command. Combine with the regular `@app.command()`.
        ```python
        @app.command()
        @app.command_alias(name="ls")
        def list(folder: Path = typer.Argument(Path.cwd(), help="Folder to list")):
            ...
        ```
        """
        return typer.Typer.command(self, *args, name=name, hidden=True, **kwargs)

    def __call__(self, *args, **kwargs):
        # initialize typer aliases
        self._init_typer_aliases(alias_help_formatter=getattr(self, 'alias_help_formatter', None),
                                 aliases_help_formatter=getattr(self, 'aliases_help_formatter', None)
        )
        # call the base class __call__ method
        super().__call__(*args, **kwargs)
        return self