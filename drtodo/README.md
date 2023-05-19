# DrTodo

**DrToDo, MD**: *a straightforward todo list manager for markdown files in git repos.*

TODO items are listed in markdown (*MD*) files using standard markdown syntax understood by most
environments including Github. You can add and modify these items easily from the command line.
Markdown files are then just committed to git as you'd normally do and shared with others or as
part of projects, or just kept locally in your computer.

## Quick Start

### installation

```console
$ pip install drtodo
```

### initialization

```console
$ todo init
```

### add a todo to the global list

```console
$ todo add "clean up folder `pwd`"
  0: 11348e9 ⚫ clean up folder /Users/me/work/src/tmp/p
```

### list todo items

```console
$ todo list
  0: 11348e9 ⚫ clean up folder /Users/me/work/src/tmp/p
```

### mark it as done

```console
$ todo done 0
  0: 11348e9 🔘 clean up folder /Users/me/work/src/tmp/p
```

### use it inside a git repo

> TODO: document this better including the git repo used with `todo init`

## Contents

- [DrTodo](#drtodo)
  - [Quick Start](#quick-start)
    - [installation](#installation)
    - [initialization](#initialization)
    - [add a todo to the global list](#add-a-todo-to-the-global-list)
    - [list todo items](#list-todo-items)
    - [mark it as done](#mark-it-as-done)
    - [use it inside a git repo](#use-it-inside-a-git-repo)
  - [Contents](#contents)
- [Markdown Files](#markdown-files)
- [Settings](#settings)
- [Command Line Options](#command-line-options)
  - [`DrTodo add`](#drtodo-add)
  - [`DrTodo debug`](#drtodo-debug)
  - [`DrTodo done`](#drtodo-done)
  - [`DrTodo init`](#drtodo-init)
  - [`DrTodo list`](#drtodo-list)
  - [`DrTodo man`](#drtodo-man)
    - [`DrTodo man config`](#drtodo-man-config)
    - [`DrTodo man mdfiles`](#drtodo-man-mdfiles)
  - [`DrTodo undone`](#drtodo-undone)
- [Configuration File Options](#configuration-file-options)
    - [Style](#style)
      - [Detailed Style Configuration](#detailed-style-configuration)
  - [Global Folder](#global-folder)
  - [Local Folder (under any git repo)](#local-folder-under-any-git-repo)
  - [Environment variables](#environment-variables)
  - [Sample config file (TOML)](#sample-config-file-toml)



# Markdown Files

By default, DrTodo will look for any lists formatted as GitHub-style task lists in any Markdown files it reads.

For example a file containing this:
```markdown
This is my cool project readme file.

## TODO
-  write a readme
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

> In the future, it will be possible to specify which section in a Markdown file to use as a list, and then all other
lists
> will be ignored.

> Also, we will have options to add to the bottom or to the top (meaning right before or right after the last task list
item).


# Settings

DrTodo allows plenty of configuration options that can be specialized by folder or per user.
There are many config files that can be used and are combined in specific ways detailed below.
Simplest case is `~/.drtodo/config.toml` which is the global config file.
More details [below](#configuration-file-options).


# Command Line Options

**Usage**:

```console
$ DrTodo [OPTIONS] COMMAND [ARGS]...
```

**Options**:

* `-s, --settings PATH`: Settings file to use  [default: /Users/USER/.drtodo]
* `-v, --verbose`: Verbose output
* `--mdfile PATH`: Markdown file to use for todo list  [default: TEST.md]
* `-V, --version`: Show version and exit
* `--install-completion`: Install completion for the current shell.
* `--show-completion`: Show completion for the current shell, to copy it or customize the installation.
* `--help`: Show this message and exit.

DrTodo can manage items in a global todo list (~/.drtodo/TEST.md) and in a local todo list (~/work/src/DrTodo/TEST.md). Settings are read from config files and env variables (see *todo man config*).

**Commands**:

* `add`: Add a new todo item to the list
* `debug`: List configuration, settings, version and...
* `done`: Mark one or more todo items as done
* `init`: Initialize DrTodo folder and files
* `list`: List todo items in the list
* `man`: Show detailed help and context for...
* `undone`: Mark one or more todo items as NOT done...

## `DrTodo add`

Add a new todo item to the list

**Usage**:

```console
$ DrTodo add [OPTIONS] DESCRIPTION
```

**Arguments**:

* `DESCRIPTION`: [required]

**Options**:

* `-p, --priority INTEGER`
* `-d, --due TEXT`: Due date in any format
* `-o, --owner TEXT`: Owner userid or name
* `-D, --done`: Add item marked as done
* `-G, --global`: Add item to global todo list, even if current folder is under a git repo
* `--help`: Show this message and exit.

## `DrTodo debug`

List configuration, settings, version and other debug info.

**Usage**:

```console
$ DrTodo debug [OPTIONS]
```

**Options**:

* `--help`: Show this message and exit.

## `DrTodo done`

Mark one or more todo items as done

**Usage**:

```console
$ DrTodo done [OPTIONS] [SPEC]
```

**Arguments**:

* `[SPEC]`: ID, index or regular expression to match item text

**Options**:

* `-i, --id TEXT`: ID of the item to mark as done
* `-n, --index INTEGER`: Index of the item to mark as done
* `-m, --match TEXT`: Regular expression to match item text
* `-a, --all`: Mark all items as done
* `--help`: Show this message and exit.

## `DrTodo init`

Initialize DrTodo folder and files

**Usage**:

```console
$ DrTodo init [OPTIONS]
```

**Options**:

* `--help`: Show this message and exit.

## `DrTodo list`

List todo items in the list

**Usage**:

```console
$ DrTodo list [OPTIONS]
```

**Options**:

* `--help`: Show this message and exit.

## `DrTodo man`

Show detailed help and context for settings, file format and heuristics

**Usage**:

```console
$ DrTodo man [OPTIONS] COMMAND [ARGS]...
```

**Options**:

* `--help`: Show this message and exit.

**Commands**:

* `config`
* `mdfiles`

### `DrTodo man config`

**Usage**:

```console
$ DrTodo man config [OPTIONS]
```

**Options**:

* `--help`: Show this message and exit.

### `DrTodo man mdfiles`

**Usage**:

```console
$ DrTodo man mdfiles [OPTIONS]
```

**Options**:

* `--help`: Show this message and exit.

## `DrTodo undone`

Mark one or more todo items as NOT done (undone)

**Usage**:

```console
$ DrTodo undone [OPTIONS] [SPEC]
```

**Arguments**:

* `[SPEC]`: ID, index or regular expression to match item text

**Options**:

* `-i, --id TEXT`: ID of the item to mark as done
* `-n, --index INTEGER`: Index of the item to mark as done
* `-m, --match TEXT`: Regular expression to match item text
* `-a, --all`: Mark all items as done
* `--help`: Show this message and exit.


# Configuration File Options

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
- 'ascii': /[ ]
- 'bright': ✅/❌
- 'check': ✓/✗
- 'boxed': ☑/☐
- 'dark': ✅/🔳
- 'light': ✅/🔲

#### Detailed Style Configuration

If you want to configure the style in more detail, you can do so with any of these options:

```toml

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

All the colors above use the rich style and color names. See (https://rich.readthedocs.io/en/latest/style.html#style)
for more info.

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
mdfile = 'TODO.md'
verbose = false
keep_backups = 3
hide_hash = false

checked = '🔘'
unchecked = '⚫'
strike_done = false
dim_done = false
index = 'bright_black'
hash = 'italic dim yellow'
text = 'white'
header = 'bold cyan'
warning = 'bold yellow'
error = 'red'

```

