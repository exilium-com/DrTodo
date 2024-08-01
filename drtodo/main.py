from pathlib import Path
from typing import Optional

import rich.markdown
import typer
# from git.repo import Repo

from typer_aliases import Typer

from . import backup_command, util
from .man_command import manapp
from .mdparser import TaskListTraverser, TodoListParser
from .rich_display import console, error_console
from . import config
from . import taskitems


app = Typer(
    no_args_is_help=True,
    rich_markup_mode="markdown",
    help=f"**{config.constants.appname}, MD**: *a straightforward todo list manager for markdown files in git repos.*",
    epilog=f"DrToDo can manage items in a global todo list (typically in {config.make_pretty_path(config.constants.appdir)})"
    f" and in a local todo list (if the current folder is under a git repo configured for {config.constants.appname})."
    f" Settings are read from config files and env variables (see *todo man config*).",
)


def version_string() -> str:
    return f"{config.constants.appname} v{config.constants.version}"


@app.command()
def init():
    """
    Initialize DrToDo folder and files (in global location, use --local to override)
    """

    if config.globals.force_local:
        config.create_local_todofile_if_possible()
    else:
        config.create_appdir_if_possible()


def print_todo_item(item: dict):
    # print a green large checkmark if checked is True or a blank empty box if checked is False
    # and properly render the markdown text with rich
    # trim trailing whitespace too
    assert isinstance(config.settings.style, config.Style)
    checked_bullet = config.settings.style.checked
    unchecked_bullet = config.settings.style.unchecked

    strike = ""
    dim = ""
    if item['checked']:
        if config.settings.style.dim_done:
            dim = "[dim]"
        if config.settings.style.strike_done:
            strike = "[strike]"

    index_part = f"[index]{dim}{strike}{item['index']:>3}: "
    hash_part = f"[hash]{dim}{strike}{item['id'][:7]} " if not config.settings.hide_hash else ""
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
            console().print(f"[header]{config.make_pretty_path(todofile)}[text]")
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

    for todofile in config.globals.todo_files:
        listfromfile(todofile)


@app.command(name="debug")
@app.command_alias(name="dbg")
def debug_command():
    """
    List configuration, settings, version and other debug info.
    """
    d = config.constants.__dict__ | dict(config.settings) | config.globals.__dict__
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
):
    """
    Add a new todo item to the list
    """
    duestr = f" due:{due}" if due else ""
    ownerstr = f" @{owner}" if owner else ""
    prioritystr = f" P{priority}" if priority else ""
    itemstr = f"{prioritystr}{ownerstr}{duestr} {description}".strip()
    todo_item = TaskListTraverser.create_item(itemstr, index=0, checked=done)
    for todo_file in config.globals.todo_files:
        if config.settings.verbose:
            console().print(f"[header]{config.make_pretty_path(todo_file)}[text]")
        _add_item(todo_item, todo_file)
    if config.settings.verbose:
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
):
    """
    Remove/delete todo items from the list
    """

    def removefromfile(todo_file: Path) -> int:
        count = 0
        if todo_file and todo_file.exists():
            if config.settings.verbose:
                console().print(f"[header]{config.make_pretty_path(todo_file)}[text]")
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
                    if config.settings.verbose:
                        print_todo_item(item)
            except Exception as e:
                error_console().print(f"no items removed: {e}")
                raise typer.Exit(2)
            finally:
                backup_command.save_with_backups(todo_file, todo)
        return count

    removed = 0
    for todo_file in config.globals.todo_files:
        removed += removefromfile(todo_file)

    if removed == 0:
        error_console().print("nothing to remove")


@app.command(name="clean")
def clean_command(just_move: bool = typer.Option(None, "--move/--remove", "-m/-r", show_default=False,
                                                 help="Cleanup method: either move to the done section or just remove items. "\
                                                 "Defaults *remove* unless a done section is set.")):
    """Cleans up the todo list, removing all done items or moving them to a done section"""

    def cleanfromfile(todo_file: Path, move: bool) -> int:
        count = 0
        if todo_file and todo_file.exists():
            if config.settings.verbose:
                fname = config.make_pretty_path(todo_file)
                console().print(f"[header]{fname}[text] - {'moving' if move else '[warning]removing[text]'} done items:")
            todo = TodoListParser()
            todo.parse(todo_file)
            try:
                items = taskitems.create_iterator(todo.items, omit_means_all=False, done=True)
            except ValueError as e:
                error_console().print(f"error: {e}")
                raise typer.Exit(2)

            try:
                # we gather then commit to process items from list we are iterating over
                to_clean = []
                for item in items:
                    to_clean.append(item)

                count = len(to_clean)
                while to_clean:
                    item = to_clean.pop(0)
                    if move:
                        raise NotImplementedError("moving done items not yet implemented")
                    else:
                        todo.remove_item(item)
                    if config.settings.verbose:
                        print_todo_item(item)
            except Exception as e:
                error_console().print(f"no items cleaned: {e}")
                raise typer.Exit(2)
            finally:
                backup_command.save_with_backups(todo_file, todo)
        return count

    if just_move is None:
        just_move = bool(config.settings.done_section)

    cleaned = 0
    for todo_file in config.globals.todo_files:
        cleaned += cleanfromfile(todo_file, just_move)

    if cleaned == 0:
        error_console().print("nothing to clean")


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
            if config.settings.verbose:
                console().print(f"[header]{config.make_pretty_path(todo_file)}[text] changes:")
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
                if config.settings.verbose:
                    print_todo_item(item)
                count += 1
            # write back to file
            backup_command.save_with_backups(todo_file, todo)
        return count

    for todo_file in config.globals.todo_files:
        doneundonefromfile(todo_file)


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
        files = config.globals.todo_files
    for file in files:
        if file and file.exists():
            if len(files) > 1:
                console().print(f"[header]{config.make_pretty_path(file)}[text]")
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


def _global_local_callback(value: bool):
    # called if either --local(value=False) or --global(value=True) is provided. If neither is provided, value is None.
    if value is not None:
        config.postclioptions_initialize(force_global=value, force_local=not value)


panel_ADVANCED = "Advanced options"


# Typer callback handles global options like --mdfile and --verbose
@app.callback()
def main_callback(
    # settings_file: Optional[Path] = typer.Option(config.constants.appdir, "--settings", "-S", help="Settings file to use",
    #                                              rich_help_panel=panel_GLOBAL),
    global_local: Optional[bool] = typer.Option(None,
        "--global/--local", "-G/-L",
        help="Force operation on global or local todo list. Default is chosen smartly: local if folder is "\
        "under a git repo initialized for DrToDo, global otherwise.",
        callback=_global_local_callback, is_eager=True, show_default=False,
        rich_help_panel=panel_ADVANCED),
    section: Optional[str] = typer.Option(None,
        help="Section name in markdown file to use for todo list, with optional "\
        "heading level, e.g. '## TODO'", show_default=False,
        rich_help_panel=panel_ADVANCED),
    done_section: Optional[str] = typer.Option(None,
        help="Section name in markdown file to use for done items, with optional "\
        "heading level, e.g. '## DONE'", show_default=False,
        rich_help_panel=panel_ADVANCED),
    reverse_order: Optional[bool] = typer.Option(config.settings.reverse_order,
        "--reverse-order/--normal-order",
        help="Whether todo items should be in reverse order (latest first)",
        rich_help_panel=panel_ADVANCED),
    mdfile: Optional[Path] = typer.Option(None,
        help="Markdown file to use for todo list", show_default=False,
        rich_help_panel=panel_ADVANCED),
    verbose: Optional[bool] = typer.Option(config.settings.verbose,
        "--verbose/--quiet", "-v/-q",
        help="Verbose or quiet output"),
    version: bool = typer.Option(False,
        "--version", "-V",
        help="Show version and exit",
        callback=_version_callback, is_eager=True),
):
    if mdfile:
        config.settings.mdfile = str(mdfile)
    if verbose:
        config.settings.verbose = verbose
    if section is not None:
        config.settings.section = section
    if done_section is not None:
        config.settings.done_section = done_section
    if reverse_order:
        config.settings.reverse_order = reverse_order


def main(*args, **kwargs):
    app(*args, **kwargs)


if __name__ == "__main__":
    main()
