import inspect
import re
from pathlib import Path
from typing import Optional, Callable

import rich.markdown
import typer
from git.repo import Repo
from rich import print

from .man_command import manapp
from .mdparser import TaskListTraverser, TodoListParser
from .rich_display import console
from .settings import constants, globals, settings, Style

app = typer.Typer(
    no_args_is_help=True,
    rich_markup_mode="markdown",
    help=f"**{constants.appname}, MD**: *a straightforward todo list manager for markdown files in git repos.*",
    epilog=f"DrTodo can manage items in a global todo list ({globals.global_todofile_pretty})"
    f" and in a local todo list ({globals.local_todofile_pretty or 'if the current folder is under a git repo'})."
    f" Settings are read from config files and env variables (see *todo man config*).",
    rich_help_panel="Integration")


def version_string() -> str:
    return f"{constants.appname} v{constants.version}"


def ensure_appdir(may_create: bool = False) -> None:
    if not constants.appdir.exists():
        if not may_create:
            print(f"DrTodo folder {constants.appdir} does not exist. Use [bold]todo init[/bold] to create it.")
        else:
            constants.appdir.mkdir(parents=False, exist_ok=False)
            assert globals.global_todofile and not globals.global_todofile.exists()
            globals.global_todofile.touch()
            repo = Repo.init(constants.appdir)
            repo.index.add([globals.global_todofile])


@app.command()
def init():
    """
    Initialize DrTodo folder and files
    """
    ensure_appdir(may_create=True)


def print_todo_item(item: dict):
    # print a green large checkmark if checked is True or a blank empty box if checked is False
    # and properly render the markdown text with rich
    # trim trailing whitespace too
    assert isinstance(settings.style, Style)
    checked_bullet = settings.style.checked
    unchecked_bullet = settings.style.unchecked

    strike = ""
    dim = ""
    if item['checked']:
        if settings.style.dim_done:
            dim = "[dim]"
        if settings.style.strike_done:
            strike = "[strike]"

    index_part = f"[index]{dim}{strike}{item['index']:>3}: "
    hash_part = f"[hash]{dim}{strike}{item['id'][:7]} " if not settings.hide_hash else ""
    checkmark_part = f"[text]{dim}{strike}{checked_bullet if item['checked'] else unchecked_bullet} "
    mdtext_part = rich.markdown.Markdown(item['text'].rstrip())
    if dim:
        mdtext_part.style = "dim"
    if strike:
        mdtext_part.style = "strike"
    console().print(index_part + hash_part + checkmark_part, mdtext_part, end='')


def print_todo_items(items: list):
    for item in items:
        print_todo_item(item)


@app.command(name="list")
@app.command(name="ls", hidden=True)
def list_command():
    """
    List todo items in the list
    """
    if globals.global_todofile and globals.global_todofile.exists():
        console().print(f"[header]{globals.global_todofile_pretty}[text]")
        todo = TodoListParser()
        todo.parse(globals.global_todofile)
        print_todo_items(todo.items)
    if globals.local_todofile and globals.local_todofile.exists():
        console().print(f"[header]{globals.local_todofile_pretty}[text]")
        todo = TodoListParser()
        todo.parse(globals.local_todofile)
        print_todo_items(todo.items)


@app.command(name="debug")
@app.command(name="dbg", hidden=True)
def debug_command():
    """
    List configuration, settings, version and other debug info.
    """
    console().print(f"{version_string()}", highlight=False)

    d = constants.__dict__ | dict(settings) | globals.__dict__
    console().print(d)


def _add_item(todo_item: dict, todofile_path: Path):
    if todofile_path and todofile_path.exists():
        todo = TodoListParser()
        todo.parse(todofile_path)
        # TODO: need to append in the MD file in the right place (once we support sections, etc.)
        todo.add_item_after(add=todo_item, after=todo.items[-1])
        save_todo_backups(todofile_path, todo)
    else:
        print(f"Cannot add item to {todofile_path} because it does not exist")
        raise typer.Exit(2)


# add [--priority <priority>] [--due <due>] [--owner <owner>] [--done] <item description>
@app.command()
def add(
    description: str,
    priority: int = typer.Option(None, "--priority", "-p"),
    due: str = typer.Option(None, "--due", "-d", help="Due date in any format"),
    owner: str = typer.Option(None, "--owner", "-o", help="Owner userid or name"),
    done: bool = typer.Option(False, "--done", "-D", help="Add item marked as done"),
    global_todo: bool = typer.Option(False, "--global", "-G",
                                     help="Add item to global todo list, even if current folder is under a git repo"),
):
    """
    Add a new todo item to the list
    """
    duestr = f" due:{due}" if due else ""
    ownerstr = f" @{owner}" if owner else ""
    prioritystr = f" P{priority}" if priority else ""
    itemstr = f"{prioritystr}{ownerstr}{duestr} {description}".strip()
    todo_item = TaskListTraverser.create_item(itemstr, index=0, checked=done)
    if not global_todo and globals.local_todofile and globals.local_todofile.exists():
        console().print(f"[header]{globals.local_todofile_pretty}[text]")
        _add_item(todo_item, globals.local_todofile)
    else:
        assert globals.global_todofile
        console().print(f"[header]{globals.global_todofile_pretty}[text]")
        _add_item(todo_item, globals.global_todofile)
    print_todo_item(todo_item)


def save_todo_backups(pathname: Path, todo):
    def make_backup_path(i: int) -> Path:
        assert isinstance(i, int) and i > 0
        # files are hidden and have a '.bak-1' extension for the most recent backup, '.bak-2' for the next, etc.
        return pathname.with_name(f".{pathname.name.removeprefix('.')}.bak-{i}")

    # first write to a temp file with a '.tmp' extension
    tmpfilepath = pathname.with_suffix(pathname.suffix + '.tmp')
    todo.write(tmpfilepath)

    # if file write worked, then we can perform the rename dance
    n = settings.keep_backups
    if n > 0:
        # we keep n backups named as '.bak-1' (for the most recent n-1 backup), '.bak-2', etc.)
        # first delete the oldest backup
        make_backup_path(n).unlink(missing_ok=True)
        for i in range(n - 1, 0, -1):
            bakfilepath = make_backup_path(i)
            if bakfilepath.exists():
                bakfilepath.rename(make_backup_path(i + 1))
        # rename the original file to '.bak-1'
        pathname.rename(make_backup_path(1))
    # finally, rename the temp file to the original filename
    tmpfilepath.rename(pathname)


def _done_undone_marker(done: bool, spec, id, index, match, all):
    """
    Mark one or more todo items as done or undone.
    """
    # ensure exactly one of spec, id, index, match or all is not None
    if sum([spec is not None, id is not None, index is not None, match is not None, all]) != 1:
        # console().print("[error]ERROR:[/error] Exactly one of --id, --index, --match or --all must be provided")
        raise typer.BadParameter("Exactly one of --id, --index, --match or --all must be provided")

    if spec is not None:
        # heuristics:
        # if spec is a small integer, assume it's an index
        # if spec is a a pure hex string assume it's an ID
        # otherwise assume it's a regular expression
        try:
            index = int(spec)
            if index >= 1000:
                raise ValueError
        except ValueError:
            if re.match(r'^[0-9a-f]+$', spec):
                id = spec
            else:
                match = spec

    def matching_items_iter(items, id, index, match, all):
        if all:
            for item in items:
                yield item
        elif id is not None:
            for item in items:
                if item['id'].startswith(id):
                    yield item
        elif index is not None:
            for item in items:
                if item['index'] == index:
                    yield item
        elif match is not None:
            for item in items:
                if re.search(match, item['text']):
                    yield item

    if globals.global_todofile and globals.global_todofile.exists():
        console().print(f"[header]{globals.global_todofile}[text] changes:")
        todo = TodoListParser()
        todo.parse(globals.global_todofile)
        for item in matching_items_iter(todo.items, id, index, match, all):
            item['checked'] = done
            print_todo_item(item)
        # write back to file
        save_todo_backups(globals.global_todofile, todo)

    if globals.local_todofile and globals.local_todofile.exists():
        console().print(f"[header]{globals.local_todofile}[text] changes:")
        todo = TodoListParser()
        todo.parse(globals.local_todofile)
        for item in matching_items_iter(todo.items, id, index, match, all):
            item['checked'] = done
            print_todo_item(item)
        # write back to file
        save_todo_backups(globals.local_todofile, todo)


# done [--id <id> | --index <index> | --all | --match <regular expression> | <specification>]
# (exactly one option must be provided)
@app.command()
def done(
    spec: str = typer.Argument(None, help="ID, index or regular expression to match item text"),
    id: str = typer.Option(None, "--id", "-i", help="ID of the item to mark as done"),
    index: int = typer.Option(None, "--index", "-n", help="Index of the item to mark as done"),
    match: str = typer.Option(None, "--match", "-m", help="Regular expression to match item text"),
    all: bool = typer.Option(False, "--all", "-a", help="Mark all items as done"),
):
    """
    Mark one or more todo items as done
    """
    _done_undone_marker(True, spec, id, index, match, all)


# undone [--id <id> | --index <index> | --all | --match <regular expression> | <specification>]
# (exactly one option must be provided)
@app.command()
def undone(
    spec: str = typer.Argument(None, help="ID, index or regular expression to match item text"),
    id: str = typer.Option(None, "--id", "-i", help="ID of the item to mark as done"),
    index: int = typer.Option(None, "--index", "-n", help="Index of the item to mark as done"),
    match: str = typer.Option(None, "--match", "-m", help="Regular expression to match item text"),
    all: bool = typer.Option(False, "--all", "-a", help="Mark all items as done"),
):
    """
    Mark one or more todo items as NOT done (undone)
    """
    _done_undone_marker(False, spec, id, index, match, all)


app.add_typer(manapp,
              name="man",
              help="Show detailed help and context for settings, file format and heuristics",
              no_args_is_help=True)


def _version_callback(value: bool) -> None:
    if value:
        print(version_string())
        raise typer.Exit()


panel_GLOBAL = "Global Options"
panel_FILESELECTION = "File Selection Options"


# Typer callback handles global options like --mdfile and --verbose
@app.callback()
def main_callback(
    settings: Optional[Path] = typer.Option(constants.appdir, "--settings", "-s", help="Settings file to use",
                                            rich_help_panel=panel_GLOBAL),
    verbose: Optional[bool] = typer.Option(False, "--verbose", "-v", help="Verbose output",
                                           rich_help_panel=panel_GLOBAL),
    mdfile: Optional[Path] = typer.Option(settings.mdfile, help="Markdown file to use for todo list",
                                          rich_help_panel=panel_FILESELECTION),
    version: Optional[bool] = typer.Option(False, "--version", "-V", help="Show version and exit",
                                           callback=_version_callback, is_eager=True, rich_help_panel=panel_GLOBAL),
):
    # BUG: this is called even when the command is init, so it prints a warning about the appdir not existing
    ensure_appdir()


# this is fairly generic code that can be used to add aliases to any typer app
# TODO: move this to a separate package and create decorators for it
# @app.command_alias(name = 'ls') on the command function
# @typer_aliases(app=app) on the main() function or maybe @app.typer_aliases()
def typer_aliases(*, app: typer.Typer,
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
        if app.rich_markup_mode == "markdown":
            return f"Alias of `{aliased_name}`"
        elif app.rich_markup_mode == "rich":
            return f"Alias of [bold]{aliased_name}[/bold]"
        else:
            return f"Alias of {aliased_name}"

    def format_aliases_help(base_help: str, aliases: list[str]) -> str:
        if app.rich_markup_mode == "markdown":
            return f"{base_help} *[or {', '.join([f'`{alias}`' for alias in aliases])}]*"
        elif app.rich_markup_mode == "rich":
            return f"{base_help} [italics][or {', '.join([f'[bold]{alias}[/bold]' for alias in aliases])}][/italics]"
        else:
            return f"{base_help} [or {', '.join(aliases)}]"

    alias_help_formatter = alias_help_formatter or format_alias_help
    aliases_help_formatter = aliases_help_formatter or format_aliases_help

    aliased_commands = set()
    # for each command that is not hidden, find any hidden command with the same callback
    for visible_command in [cmd for cmd in app.registered_commands if not cmd.hidden]:
        for hidden_command in [cmd for cmd in app.registered_commands if cmd.hidden]:
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


def main(*args, **kwargs):
    typer_aliases(app=app)
    app(*args, **kwargs)


if __name__ == "__main__":
    main()
