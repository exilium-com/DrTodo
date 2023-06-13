import time
from pathlib import Path

import typer

from typer_aliases import Typer

from .rich_display import console
from .settings import make_pretty_path, settings, globals

app = Typer()

force_operation = False
force_global = False


def make_backup_path(pathname: Path, i: int) -> Path:
    assert isinstance(i, int) and i > 0
    # files are hidden and have a '.bak-1' extension for the most recent backup, '.bak-2' for the next, etc.
    return pathname.with_name(f".{pathname.name.removeprefix('.')}.bak-{i}")


def save_with_backups(pathname: Path, todo):
    """
    Saves the todo to the given pathname, making n backups as configured.
    """
    # first write to a temp file with a '.tmp' extension
    tmpfilepath = pathname.with_suffix(pathname.suffix + '.tmp')
    todo.write(tmpfilepath)

    # if file write worked, then we can perform the rename dance
    n = settings.keep_backups
    if n > 0:
        # we keep n backups named as '.bak-1' (for the most recent n-1 backup), '.bak-2', etc.)
        # first delete the oldest backup
        make_backup_path(pathname, n).unlink(missing_ok=True)
        for i in range(n, 0, -1):
            bakfilepath = make_backup_path(pathname, i)
            if bakfilepath.exists():
                bakfilepath.rename(make_backup_path(pathname, i + 1))
        # rename the original file to '.bak-1'
        pathname.rename(make_backup_path(pathname, 1))
    # finally, rename the temp file to the original filename
    tmpfilepath.rename(pathname)


def restore_backup(pathname: Path):
    """
    Rolls back backup files by one. This can be very destructive, call with care.
    """
    # first rename the current file pathname as .tmp
    tmpfilepath = pathname.with_suffix(pathname.suffix + '.tmp')
    pathname.rename(tmpfilepath)
    try:
        # rename the most recent backup to the original filename
        make_backup_path(pathname, 1).rename(pathname)
        # then rename backups in reverse order
        for i in range(2, settings.keep_backups + 1):
            bakfilepath = make_backup_path(pathname, i)
            if bakfilepath.exists():
                bakfilepath.rename(make_backup_path(pathname, i - 1))
    finally:
        # if everything works, we can delete the .tmp file
        tmpfilepath.unlink()


def scan_backups(pathname: Path):
    n = settings.keep_backups
    if n > 0:
        for i in range(n, 0, -1):
            bakfilepath = make_backup_path(pathname, i)
            if bakfilepath.exists():
                yield i, bakfilepath


def _print_file(index, filepath: Path):
    modtime = time.ctime(filepath.stat().st_mtime)
    console().print(f"[index]{index:>3}:[/index] [hash]{modtime}[/hash] [text]{make_pretty_path(filepath)}[/text]")



@app.command()
@app.command_alias(name="ls")
def list():
    """
    Lists any existing backup files
    """
    locations = [globals.global_todofile] if force_global else [globals.global_todofile, globals.local_todofile]
    for location in locations:
        if location and location.exists():
            for i, bakfile in scan_backups(location):
                _print_file(-i, bakfile)
            _print_file('now', location)
            break   # only the first valid location is processed


@app.command()
def restore():
    """
    Rolls back backup files by one (3 levels of backup are kept by default).
    """
    locations = [globals.global_todofile] if force_global else [globals.global_todofile, globals.local_todofile]
    for location in locations:
        if location and location.exists():
            console().print(f"[warning]Restoring backup for [text]{make_pretty_path(location)}[/text] file will be overwritten![/warning]")
            if force_operation or typer.confirm("Proceed?"):
                restore_backup(location)
                _print_file('restored', location)
            else:
                console().print("[error]skipped, use --force to proceed[/error]")
            break


# handle global options
@app.callback()
def main(
    force: bool = typer.Option(False, "--force", "-f", help="Force the operation to proceed"),
    use_global: bool = typer.Option(False, "--global", "-G",
                                    help="Use global todo list, even if current folder is under a git repo"),
):
    global force_operation, force_global
    force_operation = force
    force_global = use_global
