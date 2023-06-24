from pathlib import Path
from typing import Optional

import rich.markdown
import typer
from git.repo import Repo

from typer_aliases import Typer

from . import backup_command, util
from .man_command import manapp
from .mdparser import TaskListTraverser, TodoListParser
from .rich_display import console, error_console
from .settings import Style, constants, globals, make_pretty_path, settings
from . import taskitems


app = Typer(
    no_args_is_help=True,
    rich_markup_mode="markdown",
    help=f"**{constants.appname}, MD**: *a straightforward todo list manager for markdown files in git repos.*",
    epilog=f"DrTodo can manage items in a global todo list ({globals.global_todofile_pretty})"
    f" and in a local todo list ({globals.local_todofile_pretty or 'if the current folder is under a git repo'})."
    f" Settings are read from config files and env variables (see *todo man config*).",
)


def version_string() -> str:
    return f"{constants.appname} v{constants.version}"


def ensure_appdir(may_create: bool = False) -> None:
    if not constants.appdir.exists():
        if not may_create:
            error_console().print(f"DrTodo folder {constants.appdir} does not exist. Use [bold]todo init[/bold] to create it.")
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


@app.command(name="list")
@app.command_alias(name="ls")
def list_command(
    spec: str = typer.Argument(None, help="ID, index, range or regular expression to match item text"),
    id: str = typer.Option(None, "--id", "-i", help="ID of the item to list"),
    index: int = typer.Option(None, "--index", "-n", help="Index of the item to list"),
    range: str = typer.Option(None, "--range", "-r", help="Range of item indices to list, e.g, 2:5, 2:, :5"),
    match: str = typer.Option(None, "--match", "-m", help="Regular expression to match item text"),
    # TODO: add more filter options, done/undone, priority, due, owner, etc.
):
    """
    List todo items in the list
    """

    def listfromfile(todofile: Path):
        if todofile and todofile.exists():
            console().print(f"[header]{make_pretty_path(todofile)}[text]")
            todo = TodoListParser()
            todo.parse(todofile)
            try:
                items = taskitems.create_iterator(todo.items, omit_means_all=True,
                                                  spec=spec, id=id, index=index, range=range, match=match)
            except ValueError as e:
                error_console().print(f"error: {e}")
                raise typer.Exit(2)

            for item in items:
                print_todo_item(item)

    if globals.global_todofile and globals.global_todofile.exists():
        listfromfile(globals.global_todofile)

    if globals.local_todofile and globals.local_todofile.exists():
        listfromfile(globals.local_todofile)


@app.command(name="debug")
@app.command_alias(name="dbg")
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
        backup_command.save_with_backups(todofile_path, todo)
    else:
        error_console().print(f"Cannot add item to {todofile_path} because it does not exist")
        raise typer.Exit(2)


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
        if (settings.verbose):
            console().print(f"[header]{globals.local_todofile_pretty}[text]")
        _add_item(todo_item, globals.local_todofile)
    else:
        assert globals.global_todofile
        if (settings.verbose):
            console().print(f"[header]{globals.global_todofile_pretty}[text]")
        _add_item(todo_item, globals.global_todofile)
    if (settings.verbose):
        print_todo_item(todo_item)


@app.command(name="remove")
@app.command_alias(name="rm")
def remove_command(
    spec: str = typer.Argument(None, help="ID, index, range or regular expression to match item text"),
    id: str = typer.Option(None, "--id", "-i", help="ID of the item to remove"),
    index: int = typer.Option(None, "--index", "-n", help="Index of the item to remove"),
    range: str = typer.Option(None, "--range", "-r", help="Range of item indices to remove, e.g, 2:5, 2:, :5"),
    match: str = typer.Option(None, "--match", "-m", help="Regular expression to match item text"),
    # TODO: add more filter options, done/undone, priority, due, owner, etc.
    global_todo: bool = typer.Option(False, "--global", "-G",
                                     help="Remove from global todo list, even if current folder is under a git repo"),
):
    """
    Remove/delete todo items from the list
    """

    def removefromfile(todo_file: Path) -> int:
        count = 0
        if todo_file and todo_file.exists():
            if (settings.verbose):
                console().print(f"[header]{make_pretty_path(todo_file)}[text]")
            todo = TodoListParser()
            todo.parse(todo_file)
            try:
                items = taskitems.create_iterator(todo.items, omit_means_all=False,
                                                  spec=spec, id=id, index=index, range=range, match=match)
            except ValueError as e:
                error_console().print(f"error: {e}")
                raise typer.Exit(2)

            try:
                # we gather then commit to remove from list we are iterating over
                to_remove = []
                for item in items:
                    to_remove.append(item)

                count = len(to_remove)
                while to_remove:
                    item = to_remove.pop(0)
                    todo.remove_item(item)
                    if (settings.verbose):
                        print_todo_item(item)
            except Exception as e:
                error_console().print(f"no items removed: {e}")
                raise typer.Exit(2)
            finally:
                backup_command.save_with_backups(todo_file, todo)
        return count

    if not global_todo and globals.local_todofile and globals.local_todofile.exists():
        # remove from local todo list
        removed = removefromfile(globals.local_todofile)
    elif globals.global_todofile and globals.global_todofile.exists():
        # remove from global todo list
        removed = removefromfile(globals.global_todofile)
    else:
        removed = 0

    if removed == 0:
        error_console().print("nothing to remove")


def _done_undone_marker(done: bool, spec, id, index, range, match, all):
    """
    Mark one or more todo items as done or undone.
    """
    # ensure exactly one of spec, id, index, match or all is not None
    if sum([spec is not None, id is not None, index is not None, range is not None, match is not None, all]) != 1:
        raise typer.BadParameter("Exactly one of --id, --index, --range, --match or --all must be provided")

    def doneundonefromfile(todo_file: Optional[Path]) -> int:
        count = 0
        if todo_file and todo_file.exists():
            if (settings.verbose):
                console().print(f"[header]{make_pretty_path(todo_file)}[text] changes:")
            todo = TodoListParser()
            todo.parse(todo_file)
            try:
                items = taskitems.create_iterator(todo.items, omit_means_all=False,
                                                  spec=spec, id=id, index=index, range=range, match=match) if not all else todo.items
            except ValueError as e:
                error_console().print(f"error: {e}")
                raise typer.Exit(2)

            for item in items:
                item['checked'] = done
                if (settings.verbose):
                    print_todo_item(item)
                count += 1
            # write back to file
            backup_command.save_with_backups(todo_file, todo)
        return count

    doneundonefromfile(globals.global_todofile)
    doneundonefromfile(globals.local_todofile)


# done [--id <id> | --index <index> | --all | --match <regular expression> | <specification>]
# (exactly one option must be provided)
@app.command()
def done(
    spec: str = typer.Argument(None, help="ID, index, range or regular expression to match item text"),
    id: str = typer.Option(None, "--id", "-i", help="ID of the item to mark"),
    index: int = typer.Option(None, "--index", "-n", help="Index of the item to mark"),
    range: str = typer.Option(None, "--range", "-r", help="Range of item indices to mark, e.g, 2:5, 2:, :5"),
    match: str = typer.Option(None, "--match", "-m", help="Regular expression to match item text"),
    all: bool = typer.Option(False, "--all", "-a", help="Mark all items"),
):
    """
    Mark one or more todo items as done
    """
    _done_undone_marker(True, spec, id, index, range, match, all)


# undone [--id <id> | --index <index> | --all | --match <regular expression> | <specification>]
# (exactly one option must be provided)
@app.command()
def undone(
    spec: str = typer.Argument(None, help="ID, index, range or regular expression to match item text"),
    id: str = typer.Option(None, "--id", "-i", help="ID of the item to mark"),
    index: int = typer.Option(None, "--index", "-n", help="Index of the item to mark"),
    range: str = typer.Option(None, "--range", "-r", help="Range of item indices to mark,e.g, 2:5, 2:, :5"),
    match: str = typer.Option(None, "--match", "-m", help="Regular expression to match item text"),
    all: bool = typer.Option(False, "--all", "-a", help="Mark all items"),
):
    """
    Mark one or more todo items as NOT done (undone)
    """
    _done_undone_marker(False, spec, id, index, range, match, all)


@app.command()
def show(files: Optional[list[Path]] = typer.Argument(None, help="override which markdown files to show"),
         raw: bool = typer.Option(False, "--raw", help="Print the raw markdown man content")
        ):
    """
    Show markdown file(s) with rich rendering. Defaults to the active, configured files.
    """
    md_print = util.print_md_as_raw if raw else util.print_md_pretty
    if not files:
        files = [x for x in [globals.global_todofile, globals.local_todofile] if x]
    for file in files:
        if file and file.exists():
            if len(files) > 1:
                console().print(f"[header]{make_pretty_path(file)}[text]")
            with file.open() as f:
                mdstring = f.read()
                md_print(mdstring)


app.add_typer(manapp,
              name="man",
              help="Show detailed help and context for settings, file format and heuristics",
              no_args_is_help=True)


app.add_typer(backup_command.app,
              name="backup",
              help="Manage backups of markdown files",
              no_args_is_help=True)


def _version_callback(value: bool) -> None:
    if value:
        console().print(f"{version_string()}", highlight=False)
        raise typer.Exit()


panel_FILESELECTION = "File Selection Options"


# Typer callback handles global options like --mdfile and --verbose
@app.callback()
def main_callback(
    # settings_file: Optional[Path] = typer.Option(constants.appdir, "--settings", "-S", help="Settings file to use",
    #                                              rich_help_panel=panel_GLOBAL),
    verbose: bool = typer.Option(settings.verbose, "--verbose/--quiet", "-v/-q", help="Verbose or quiet output"),
    mdfile: Path = typer.Option(settings.mdfile, help="Markdown file to use for todo list",
                                rich_help_panel=panel_FILESELECTION),
    section: str = typer.Option(settings.section,
                                help="Section name in markdown file to use for todo list, with optional "\
                                "heading level, e.g. '## TODO'",
                                rich_help_panel=panel_FILESELECTION),
    reverse_order: bool = typer.Option(settings.reverse_order, "--reverse-order/--normal-order",
                                       help="Whether todo items should be in reverse order (latest first)",
                                       rich_help_panel=panel_FILESELECTION),
    version: bool = typer.Option(False, "--version", "-V", help="Show version and exit",
                                 callback=_version_callback, is_eager=True),
):
    settings.mdfile = str(mdfile)
    settings.verbose = verbose
    settings.section = section
    settings.reverse_order = reverse_order

    # BUG: this is called even when the command is init, so it prints a warning about the appdir not existing
    ensure_appdir()


def main(*args, **kwargs):
    app(*args, **kwargs)


if __name__ == "__main__":
    main()
