import os
import getpass
from dataclasses import dataclass
from pathlib import Path
from typing import Optional, Any, Union

import typer
from pydantic import BaseModel, BaseSettings, Field

try:
    import tomllib as toml
except ImportError:
    import tomli as toml
from git.repo import Repo

from . import __version__
from .rich_display import console, error_console

__all__ = ["constants", "settings", "globals", "postclioptions_initialize", "make_pretty_path", "Style"]


@dataclass(frozen=True)
class Constants:
    appname: str = "DrToDo"
    appdir: Path = Path(typer.get_app_dir(appname, force_posix=True))
    version: str = __version__
    env_prefix = appname.upper() + "_"
    username: str = getpass.getuser()


constants: Constants = Constants()


class Style(BaseModel):
    checked: str = '🔘'
    unchecked: str = '⚫'
    strike_done: bool = False
    dim_done: bool = False
    index: str = 'bright_black'
    hash: str = 'italic dim yellow'
    text: str = 'white'
    header: str = 'bold cyan'
    warning: str = 'bold yellow'
    error: str = 'red'


styles = {
    '': Style(checked='🔘', unchecked='⚫'),
    'round': Style(checked='🔘', unchecked='⚫'),
    'ascii': Style(checked='\[x]', unchecked='\[ ]'),
    'bright': Style(checked='✅', unchecked='❌'),
    'check': Style(checked='✓', unchecked='✗'),
    'boxed': Style(checked='☑', unchecked='☐'),
    'dark': Style(checked='✅', unchecked='🔳'),
    'light': Style(checked='✅', unchecked='🔲'),
}


class Settings(BaseSettings):
    mdfile: str = Field('TODO.md', env=constants.env_prefix + 'MDFILE')
    section: str = Field('', env=constants.env_prefix + 'SECTION')
    reverse_order: bool = Field(False, env=constants.env_prefix + 'REVERSE_ORDER')
    verbose: bool = True
    keep_backups: int = 3   # number of backups to keep
    hide_hash: bool = False
    style: Union[Style, str] = ''

    # def __init__(self, **kwargs):
    #     super().__init__(**kwargs)
    #     self.update_values()

    def update_values(self):
        if isinstance(self.style, str):
            self.style = styles[self.style]

    class Config:
        env_prefix = constants.env_prefix
        # fields = {
        #     'mdfile': {
        #         'env': ['TODO_mdfile', 'mdfile']
        #     }
        # }


settings: Settings = None # type: ignore


class Globals:
    todo_files: list[Path] = []
    """List of todo files to operate on, in priority order."""

globals: Globals = Globals()


class Internals:
    local_mode: bool = False
    ignore_config: bool = False
    gitroot: Optional[Path] = None
    """Path to the root of the git repo, if any."""
    global_todofile: Optional[Path] = None
    local_todofile: Optional[Path] = None

internals: Internals = Internals()


def _load_config(config_folder: Path, config_filename: Path) -> dict[str, Any]:
    """
    Load config file from config folder, if it exists, and overlay with user specific config file if it exists there as well.
    Returns an empty dict if nothing is found.
    """
    result = {}
    if config_folder.exists() and config_folder.is_dir():
        config_file = config_folder / config_filename.name
        config_file_user = config_folder / f"{config_filename.stem}.{constants.username}.{config_filename.suffix}"

        if config_file.exists():
            result |= toml.loads(config_file.read_text())
        if config_file_user.exists():
            result |= toml.loads(config_file_user.read_text())
    return result


def make_pretty_path(path: Optional[Path]) -> Optional[Path]:
    """Make a path pretty by replacing the home folder with ~ if possible/needed."""
    if path:
        try:
            return '~' / path.relative_to(Path.home())
        except ValueError:
            pass

    return path


def preclioptions_initialize(*, force_global: bool = False):
    # TODO: this needs to be different perhaps. Some command line options need to be read first because they decide where
    # to look for config files or not.

    config_dict: dict[str, Any] = {}

    internals.ignore_config = os.environ.get(constants.env_prefix + 'IGNORE_CONFIG', 'false').lower() == 'true'

    internals.gitroot = None
    if not force_global:
        # find root of git repo
        try:
            repo = Repo(None, search_parent_directories=True)
            # found repo root, read local config file there
            internals.gitroot = Path(repo.git_dir).parent
            # print(f"found git at {globals.gitroot}")
        except Exception:
            # print("not under a git repo")
            pass

    internals.local_mode = False
    if internals.gitroot:
        loaded = _load_config(internals.gitroot, Path(".drtodo.toml"))
        if loaded:  # if under git repo and configured for drtodo, use local mode
            internals.local_mode = True
        if not internals.ignore_config:
            config_dict |= loaded

    if not internals.local_mode and not internals.ignore_config:
        # load either config.toml or config.{username}.toml
        config_dict |= _load_config(constants.appdir, Path("config.toml"))

    global settings
    settings = Settings(**config_dict)
    settings.update_values()
    # command line options are processed later and will override anything

    internals.global_todofile = constants.appdir / settings.mdfile
    internals.local_todofile = internals.gitroot / settings.mdfile if internals.gitroot else None

    if internals.local_mode:
        if internals.local_todofile is not None and internals.local_todofile.exists():
            # operate on local todo list
            globals.todo_files = [internals.local_todofile]
        else:
            error_console().print(f"error: local todo file {make_pretty_path(internals.local_todofile)} does not exist")
            raise typer.Exit(2)
    else:
        if not constants.appdir.exists():
            # we may operate without a global config folder, but not in global mode
            error_console().print(f"DrToDo folder {constants.appdir} does not exist. Use [bold]todo init[/bold] to create it.")
            raise typer.Exit(2)

        if internals.global_todofile is not None and internals.global_todofile.exists():
            # operate from global todo list
            globals.todo_files = [internals.global_todofile]
        else:
            error_console().print(f"error: global todo file {make_pretty_path(internals.global_todofile)} does not exist")
            raise typer.Exit(2)


def postclioptions_initialize(*, force_global: bool):
    # Called after global options have been processed may override some settings or require reinitialization.

    # Initializes the todo_files list with the appropriate files to operate on, in priority order.
    # In the future, some commands may operate on all of them (typically the least destructive ones),
    # others on just the first one (usually more destructive).

    if force_global and internals.local_mode:
        # we initialized the local mode, but the user wants to operate on the global todo file
        preclioptions_initialize(force_global=True)


def create_appdir_if_possible() -> bool:
    """Create the appdir if it doesn't exist. Return True if it was created, False otherwise."""
    if not constants.appdir.exists():
        constants.appdir.mkdir(parents=False, exist_ok=False)
        assert internals.global_todofile and not internals.global_todofile.exists()
        internals.global_todofile.touch()
        repo = Repo.init(constants.appdir)
        repo.index.add([internals.global_todofile])
        if settings.verbose:
            console().print(f"initialized {make_pretty_path(constants.appdir)}")
        return True

    if settings.verbose:
        error_console().print(f"[warning]{make_pretty_path(constants.appdir)} already exists")
    return False


def create_local_todofile_if_possible() -> bool:
    """Create a local todo config file and a blank todo file if we are under a git repo. Return True if it was created, False otherwise."""
    if internals.gitroot is not None:
        local_config_path = internals.gitroot / ".drtodo.toml"
        local_todofile = internals.gitroot / Settings().mdfile  # use default name
        if not local_todofile.exists() and not local_config_path.exists():
            internals.local_todofile.touch()
            local_config_path.write_text(get_default_config())
            # TODO: we could easily add them to the git repo. But that could mess with their commits.
            if settings.verbose:
                console().print(f"initialized {make_pretty_path(internals.gitroot)}")
            return True
        else:
            if settings.verbose:
                error_console().print(f"[warning]{make_pretty_path(local_config_path)} or {make_pretty_path(local_todofile)} already exist")
    else:
        if settings.verbose:
            error_console().print(f"[warning]not under a git repo (required for local todo file)")
    return False


def get_default_config() -> str:
    # This is NOT a general purpose TOML export. Works for this specific case only.
    # We don't need to write TOML in most cases anyway, and Python 3.11 has read only TOML support.
    x = ''
    defaults = Settings().dict()
    for k, v in defaults.items():
        if isinstance(v, dict):
            x += f"[{k}]\n"
            for k2, v2 in v.items():
                if isinstance(v2, bool):
                    tomlv = 'true' if v2 else 'false'
                elif isinstance(v2, str):
                    tomlv = repr(v2)
                else:
                    tomlv = str(v2)
                x += f"{k2} = {tomlv}\n"
        else:
            if isinstance(v, bool):
                tomlv = 'true' if v else 'false'
            elif isinstance(v, str):
                tomlv = repr(v)
            else:
                tomlv = str(v)
            x += f"{k} = {tomlv}\n"
    return x


preclioptions_initialize()  # HACK: need to initialize this before main() is called
