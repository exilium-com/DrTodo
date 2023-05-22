import typer
import rich
import rich.markdown
from .rich_display import console
from .settings import constants, get_default_config


man_output = None
manapp = typer.Typer()


def md_mdfiles():
    return f"""
# Markdown Files

By default, {constants.appname} will look for any lists formatted as GitHub-style task lists in
any Markdown files it reads.

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

> In the future, it will be possible to specify which section in a Markdown file to use as a list,
> and then all other lists will be ignored.

> Also, we will have options to add to the bottom or to the top (meaning right before or right after the
> last task list item).

"""


def md_config():
    return f"""
# Settings

DrTodo allows plenty of configuration options that can be specialized by folder or per user.
There are many config files that can be used and are combined in specific ways detailed below.
Simplest case is `~/.drtodo/config.toml` which is the global config file.

## All Options

The primary options are below with their default values. You can override any of these in a toml config file.

```toml
    mdfile = 'TODO.md'      # default markdown file to use
    verbose = false         # verbose output
    keep_backups = 3        # number of old md file backups to keep
    hide_hash = false       # don't show hash (use index or RE instead)
```


### Style

Style can be either configured at a high level by name or configured in detailed individual settings.
High level configuration is easy, just set the `style` option as follows:

```toml
style = 'round'
```

Valid options for style are:

- 'round': 🔘/⚫
- 'ascii': [x]/[ ]
- 'bright': ✅/❌
- 'check': ✓/✗
- 'boxed': ☑/☐
- 'dark': ✅/🔳
- 'light': ✅/🔲

#### Detailed Style Configuration

If you want to configure the style in more detail, you can do so with any of these options:

```toml
[style]
checked = '🔘'              # emoji or symbols used for done items
unchecked = '⚫'            # emoji or symbols used for undone items
strike_done = False         # strike through done items
dim_done = False            # dim done items
index = 'bright_black'      # color of index
hash = 'italic dim yellow'  # color of hash
text = 'white'              # color of TODO text
header = 'bold cyan'        # color of header
warning = 'bold yellow'     # color of warnings
error = 'red'               # color of errors
```

All the colors above use the rich style and color names.
See [rich docs](https://rich.readthedocs.io/en/latest/style.html#style) for more info.

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
{get_default_config()}
```
"""


@manapp.command()
def mdfiles():
    assert man_output
    man_output(md_mdfiles())


@manapp.command()
def config():
    assert man_output
    man_output(md_config())


@manapp.command()
def all():
    assert man_output
    man_output(md_mdfiles() + "\n\n" + md_config())


def output_as_raw(mdstring: str):
    console().print(mdstring, markup=False, highlight=False)

def output_pretty(mdstring: str):
    console().print(rich.markdown.Markdown(mdstring))

# handle global options
@manapp.callback()
def main(
    raw: bool = typer.Option(False, "--raw", help="Print the raw markdown man content"),
):
    global man_output
    man_output = output_as_raw if raw else output_pretty
