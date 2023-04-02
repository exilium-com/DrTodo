from __future__ import annotations
import os
from pathlib import Path
from dataclasses import dataclass
from typing import Any, Optional
import typer
from pydantic import BaseSettings, Field
try:
    import tomllib as toml
except ImportError:
    import tomli as toml
from git import Repo


__all__ = ["constants", "settings", "globals", "initialize"]


@dataclass(frozen=True)
class Constants:
    appname: str = "DrTodo"
    appdir: Path = Path(typer.get_app_dir(appname, force_posix=True))
    version: str = "0.1.0"
    env_prefix = appname.upper() + "_"
    username: str = os.getlogin()


constants: Constants = Constants()


class Settings(BaseSettings):
    mdfile: str = Field("TODO.md", env=constants.env_prefix + "MDFILE")
    verbose: bool = False

    class Config:
        env_prefix = constants.env_prefix
        # fields = {
        #     'mdfile': {
        #         'env': ['TODO_mdfile', 'mdfile']
        #     }
        # }


settings: Settings


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


def make_pretty_path(path: Path) -> str:

    return '~' / path.relative_to(Path.home())

def initialize():
    # TODO: this needs to be different perhaps. Some command line options need to be read first because they decide where
    # to look for config files or not.
    # TODO: Also, settings in the gitroot folder may override settings in the appfolder and that may not be expected. Perhaps
    # we need gitroo settings to only apply to to the gitroot TODO file and not to the appfolder TODO file?

    # Folder structure:
    #   ~/.drtodo/config.toml         global config
    #   ~/.drtoto/config.bcs.toml     user specific config (in case this folder is shared)
    #   ~/.drtodo/TODO.md             default location for todo list (configurable, and there could be more)
    #   ~/.drtodo/.git                git repo for todo list (can be shared)
    #   /somefolder/.git              root folder for nearest .git repo (TODO: support git submodules etc.?)
    #   /somefolder/.drtodo.toml      local config file for this git repo (configurable)
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

    config_dict |= load_config(constants.appdir, Path(".drtodo.toml"))

    # find root of git repo
    try:
        repo = Repo(None, search_parent_directories=True)
        # found repo root, read local config file there
        globals.gitroot = Path(repo.git_dir).parent
        # print(f"found git at {globals.gitroot}")
    except Exception:
        # print("not under a git repo")
        pass

    if globals.gitroot:
        config_dict |= load_config(globals.gitroot, Path(".drtodo.toml"))

    settings = Settings(**config_dict)
    # command line options are processed later and will override anything

    globals.global_todofile = constants.appdir / settings.mdfile
    globals.global_todofile_pretty = make_pretty_path(globals.global_todofile)
    globals.local_todofile = globals.gitroot / settings.mdfile if globals.gitroot else None
    globals.local_todofile_pretty = make_pretty_path(globals.local_todofile) if globals.local_todofile else None