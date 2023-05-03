import typer
import rich
import rich.markdown
from rich_display import console
import settings


app = typer.Typer()


@app.command()
def mdfiles():
    md = rich.markdown.Markdown(f"""
# Markdown Files

By default, {settings.constants.appname} will look for any lists formatted as GitHub-style task lists in any Markdown files it reads.

For example a file containing this:
```markdown
This is my cool project readme file.

## TODO
- [x] write a readme
- [ ] make it useful

## Bugs assigned to me
- [ ] bug 1
- [ ] bug 2
```

Will produce the following output:
```console
$ todo list
~/work/src/DrTodo/TODO.md
  0: 56a01da 🔘 write a readme
  1: 5869ea7 ⚫ make it useful
  2: 7a787ec ⚫ bug 1
  3: f237ece ⚫ bug 2
```

All items will be logically combined into a single list and listed together.

> In the future, it will be possible to specify which section in a Markdown file to use as a list, and then all other lists
> will be ignored.

> Also, we will have options to add to the bottom or to the top (meaning right before or right after the last task list item).

""")
    console.print(md)


@app.command()
def config():
    md = rich.markdown.Markdown(f"""
# Settings

## Global Folder
- `~/.drtodo`                     global config folder
- `~/.drtodo/config.toml`         global config
- `~/.drtodo/config.USER.toml`    user specific config (in case this folder is shared)
- `~/.drtodo/TODO.md`             default location for todo list (configurable, and there could be more)
- `~/.drtodo/.git`                git repo for todo list (can be shared)

## Local Folder (under any git repo)
- `/somefolder/.git`              root folder for nearest .git repo (submodules NOT supported yet)
- `/somefolder/.drtodo.toml`      local config file for this git repo (safe to commit)
- `/somefolder/.drtodo.USER.toml` local config file for this git repo (safe to commit, ignored by other users)
- `/somefolder/TODO.md`           default location for todo list for this git repo (configurable)

## Environment variables

- `DRTODO_MDFILE`                default location for todo list
- `DRTODO_VERBOSE`               verbose output

## Sample config file (TOML)
```toml
{settings.get_default_config()}
```
""")
    console.print(md)


if __name__ == "__main__":
    app()
