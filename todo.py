from typing import Optional
from pathlib import Path
import settings
import typer
from rich import print
from mdparser import parse_todo_list
from git import Repo
import rich.markdown
import re
import help_command
from rich_display import console


settings.initialize()  # HACK: need to initialize this before main() is called

app = typer.Typer(no_args_is_help=True,
                  rich_markup_mode="markdown",
                  help="**DrTodo, MD**: *a straightforward todo list manager for markdown files in git repos.*",
                  epilog=f"DrTodo can manage items in a global todo list ({settings.globals.global_todofile_pretty})"
                  f" and in a local todo list ({settings.globals.local_todofile_pretty or 'if the current folder is under a git repo'}).",
                  rich_help_panel="Integration")


def version_string() -> str:
    return f"{settings.constants.appname} v{settings.constants.version}"


def ensure_appdir(may_create: bool = False) -> None:
    if not settings.constants.appdir.exists():
        if not may_create:
            print(f"DrTodo folder {settings.constants.appdir} does not exist. Use todo init to create it.")
        else:
            settings.constants.appdir.mkdir(parents=False, exist_ok=False)
            assert settings.globals.global_todofile and not settings.globals.global_todofile.exists()
            settings.globals.global_todofile.touch()
            repo = Repo.init(settings.constants.appdir)
            repo.index.add([settings.globals.global_todofile])


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
    highlighted_md = rich.markdown.Markdown(item['text'].rstrip())
#        console.print(f"{'✅' if item['checked'] else '🔳'} ", highlighted_md, end='')
    console.print(f"[index]{item['index']:>3}: [hash]{item['id'][:7]} [text]{'🔘' if item['checked'] else '⚫'} ", highlighted_md, end='')
    # TODO: options to render todo/done items differently, e.g. strikethrough, different bullets, dim colors etc.


def print_todo_items(items: list):
    for item in items:
        print_todo_item(item)


@app.command()
def list():
    """
    List todo items in the list
    """
    if settings.globals.global_todofile and settings.globals.global_todofile.exists():
        print(f"{settings.globals.global_todofile}")
        items = parse_todo_list(settings.globals.global_todofile)
        print_todo_items(items)
    if settings.globals.local_todofile and settings.globals.local_todofile.exists():
        print(f"{settings.globals.local_todofile}")
        items = parse_todo_list(settings.globals.local_todofile)
        print_todo_items(items)


@app.command()
def debug():
    """
    List configuration, settings, version and other debug info.
    """
    console.print(f"{version_string()}")

    d = settings.constants.__dict__ | dict(settings.settings) | settings.globals.__dict__
    print(d)


# add [--priority <priority>] [--due <due>] [--owner <owner>] [--done] <item description>
@app.command()
def add(
    description: str,
    priority: int = typer.Option(None, "--priority", "-p"),
    due: str = typer.Option(None, "--due", "-d", help="Due date in any format"),
    owner: str = typer.Option(None, "--owner", "-o", help="Owner userid or name"),
    done: bool = typer.Option(False, "--done", "-D", help="Mark item as done"),
):
    """
    Add a new todo item to the list
    """
    duestr = f" due:{due}" if due else ""
    ownerstr = f" @{owner}" if owner else ""
    prioritystr = f" P{priority}" if priority else ""
    itemstr = f"{prioritystr}{ownerstr}{duestr} {description}"
    todo_item = {'checked': done, 'text': itemstr}
    print_todo_item(todo_item)


# done [--id <id> | --index <index> | --all | --match <regular expression>] (exactly one option must be provided)
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
    # ensure exactly one of spec, id, index, match or all is not None
    if sum([spec is not None, id is not None, index is not None, match is not None, all]) != 1:
        # console.print("[error]ERROR:[/error] Exactly one of --id, --index, --match or --all must be provided")
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

    if settings.globals.global_todofile and settings.globals.global_todofile.exists():
        print(f"{settings.globals.global_todofile}")
        items = parse_todo_list(settings.globals.global_todofile)
        for item in matching_items_iter(items, id, index, match, all):
            item['checked'] = True
            print_todo_item(item)
            # TODO: write back to file
    if settings.globals.local_todofile and settings.globals.local_todofile.exists():
        print(f"{settings.globals.local_todofile}")
        items = parse_todo_list(settings.globals.local_todofile)
        for item in matching_items_iter(items, id, index, match, all):
            item['checked'] = True
            print_todo_item(item)
            # TODO: write back to file


app.add_typer(help_command.app,
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
def main(
    settings: Optional[Path] = typer.Option(settings.constants.appdir, "--settings", "-s", help="Settings file to use", rich_help_panel=panel_GLOBAL),
    verbose: Optional[bool] = typer.Option(False, "--verbose", "-v", help="Verbose output", rich_help_panel=panel_GLOBAL),
    mdfile: Optional[Path] = typer.Option(settings.settings.mdfile, help="Markdown file to use for todo list", rich_help_panel=panel_FILESELECTION),
    version: Optional[bool] = typer.Option(False, "--version", "-V", help="Show version and exit", callback=_version_callback, is_eager=True, rich_help_panel=panel_GLOBAL),
):
    # BUG: this is called even when the command is init, so it prints a warning about the appdir not existing
    ensure_appdir()


if __name__ == "__main__":
    app()
