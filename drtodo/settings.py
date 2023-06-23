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
from git import Repo

from . import __version__

__all__ = ["constants", "settings", "globals", "initialize", "make_pretty_path", "Style"]


@dataclass(frozen=True)
class Constants:
    appname: str = "DrTodo"
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
    verbose: bool = False
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


settings: Settings = None


class Globals:
    gitroot: Optional[Path] = None
    global_todofile: Optional[Path] = None
    global_todofile_pretty: Optional[str] = None
    local_todofile: Optional[Path] = None
    local_todofile_pretty: Optional[str] = None


globals = Globals()


def load_config(config_folder: Path, config_filename: Path) -> dict[str, Any]:
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


def make_pretty_path(path: Path) -> Path:
    """Make a path pretty by replacing the home folder with ~ if possible/needed."""
    try:
        return '~' / path.relative_to(Path.home())
    except ValueError:
        return path


def initialize():
    # TODO: this needs to be different perhaps. Some command line options need to be read first because they decide where
    # to look for config files or not.
    # TODO: Also, settings in the gitroot folder may override settings in the appfolder and that may not be expected. Perhaps
    # we need gitroot settings to only apply to to the gitroot TODO file and not to the appfolder TODO file?

    # Folder structure:
    #   ~/.drtodo/config.toml         global config
    #   ~/.drtoto/config.bcs.toml     user specific config (in case this folder is shared)
    #   ~/.drtodo/TODO.md             default location for todo list (configurable, and there could be more)
    #   ~/.drtodo/.git                git repo for todo list (can be shared)
    #   /somefolder/.git              root folder for nearest .git repo (TODO: support git submodules etc.?)
    #   /somefolder/.drtodo.toml      local config file for this git repo (configurable)
    #   /somefolder/.drtodo.bcs.toml  local config file for this git repo (configurable)
    #   /somefolder/TODO.md           default location for todo list for this git repo (configurable)
    # environment variables:
    #  DRTODO_MDFILE                 default location for todo list
    #  DRTODO_VERBOSE                verbose output

    # configuration hierarchy is read in this order (later overrides earlier):
    # 1. read global config file
    # 2. read user specific config file
    # 3. red local config file (root of git repo, if any)
    # 4. read environment variables (this is implicit in pydantic)
    # 5. read command line options

    global settings
    config_dict: dict[str, Any] = {}

    do_load = os.environ.get(constants.env_prefix + 'IGNORE_CONFIG', 'false').lower() != 'true'

    if do_load:
        # load either config.toml or config.{username}.toml
        config_dict |= load_config(constants.appdir, Path("config.toml"))

    # find root of git repo
    try:
        repo = Repo(None, search_parent_directories=True)
        # found repo root, read local config file there
        globals.gitroot = Path(repo.git_dir).parent
        # print(f"found git at {globals.gitroot}")
    except Exception:
        # print("not under a git repo")
        pass

    if do_load and globals.gitroot:
        config_dict |= load_config(globals.gitroot, Path(".drtodo.toml"))

    settings = Settings(**config_dict)
    settings.update_values()
    # command line options are processed later and will override anything

    globals.global_todofile = constants.appdir / settings.mdfile
    globals.global_todofile_pretty = make_pretty_path(globals.global_todofile)
    globals.local_todofile = globals.gitroot / settings.mdfile if globals.gitroot else None
    globals.local_todofile_pretty = make_pretty_path(globals.local_todofile) if globals.local_todofile else None


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


initialize()  # HACK: need to initialize this before main() is called
