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
    rich_help_panel="Integration")


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
@app.command(name="ls", hidden=True)
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
    if globals.global_todofile and globals.global_todofile.exists():
        console().print(f"[header]{globals.global_todofile_pretty}[text]")
        todo = TodoListParser()
        todo.parse(globals.global_todofile)
        for item in taskitems.task_iterator(todo.items, omit_means_all=True,
                                            spec=spec, id=id, index=index, range=range, match=match):
            print_todo_item(item)

    if globals.local_todofile and globals.local_todofile.exists():
        console().print(f"[header]{globals.local_todofile_pretty}[text]")
        todo = TodoListParser()
        todo.parse(globals.local_todofile)
        for item in taskitems.task_iterator(todo.items, omit_means_all=True,
                                            spec=spec, id=id, index=index, range=range, match=match):
            print_todo_item(item)


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
        backup_command.save_with_backups(todofile_path, todo)
    else:
        error_console().print(f"Cannot add item to {todofile_path} because it does not exist")
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

def _done_undone_marker(done: bool, spec, id, index, range, match, all):
    """
    Mark one or more todo items as done or undone.
    """
    # ensure exactly one of spec, id, index, match or all is not None
    if sum([spec is not None, id is not None, index is not None, range is not None, match is not None, all]) != 1:
        raise typer.BadParameter("Exactly one of --id, --index, --range, --match or --all must be provided")

    if globals.global_todofile and globals.global_todofile.exists():
        console().print(f"[header]{globals.global_todofile}[text] changes:")
        todo = TodoListParser()
        todo.parse(globals.global_todofile)
        items = taskitems.task_iterator(todo.items, id=id, index=index, range=range, match=match) if not all else todo.items
        for item in items:
            item['checked'] = done
            print_todo_item(item)
        # write back to file
        backup_command.save_with_backups(globals.global_todofile, todo)

    if globals.local_todofile and globals.local_todofile.exists():
        console().print(f"[header]{globals.local_todofile}[text] changes:")
        todo = TodoListParser()
        todo.parse(globals.local_todofile)
        items = taskitems.task_iterator(todo.items, id=id, index=index, range=range, match=match) if not all else todo.items
        for item in items:
            item['checked'] = done
            print_todo_item(item)
        # write back to file
        backup_command.save_with_backups(globals.local_todofile, todo)


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
        files = [globals.global_todofile, globals.local_todofile]
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


panel_GLOBAL = "Global Options"
panel_FILESELECTION = "File Selection Options"


# Typer callback handles global options like --mdfile and --verbose
@app.callback()
def main_callback(
    # settings_file: Optional[Path] = typer.Option(constants.appdir, "--settings", "-S", help="Settings file to use",
    #                                              rich_help_panel=panel_GLOBAL),
    verbose: Optional[bool] = typer.Option(settings.verbose, "--verbose", "-v", help="Verbose output",
                                           rich_help_panel=panel_GLOBAL),
    mdfile: Optional[Path] = typer.Option(settings.mdfile, help="Markdown file to use for todo list",
                                          rich_help_panel=panel_FILESELECTION),
    section: Optional[str] = typer.Option(settings.section,
                                          help="Section name in markdown file to use for todo list, with optional "\
                                          "heading level, e.g. '## TODO'",
                                          rich_help_panel=panel_FILESELECTION),
    reverse_order: Optional[bool] = typer.Option(settings.reverse_order, "--reverse-order/--normal-order",
                                                 help="Whether todo items should be in reverse order (latest first)",
                                                 rich_help_panel=panel_FILESELECTION),
    version: Optional[bool] = typer.Option(False, "--version", "-V", help="Show version and exit",
                                           callback=_version_callback, is_eager=True, rich_help_panel=panel_GLOBAL),
):
    settings.mdfile = mdfile
    settings.verbose = verbose
    settings.section = section
    settings.reverse_order = reverse_order

    # BUG: this is called even when the command is init, so it prints a warning about the appdir not existing
    ensure_appdir()


def main(*args, **kwargs):
    # typer_aliases(app=app)
    app(*args, **kwargs)


if __name__ == "__main__":
    main()
