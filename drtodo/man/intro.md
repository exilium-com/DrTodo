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
  - [All Options](#all-options)
    - [Style](#style)
      - [Detailed Style Configuration](#detailed-style-configuration)
  - [Global Folder](#global-folder)
  - [Local Folder (under any git repo)](#local-folder-under-any-git-repo)
  - [Environment variables](#environment-variables)
  - [Sample config file (TOML)](#sample-config-file-toml)
- [`DrToDo`](#drtodo-1)
  - [`DrToDo add`](#drtodo-add)
  - [`DrToDo backup`](#drtodo-backup)
    - [`DrToDo backup list`](#drtodo-backup-list)
    - [`DrToDo backup ls`](#drtodo-backup-ls)
    - [`DrToDo backup restore`](#drtodo-backup-restore)
  - [`DrToDo dbg`](#drtodo-dbg)
  - [`DrToDo debug`](#drtodo-debug)
  - [`DrToDo done`](#drtodo-done)
  - [`DrToDo init`](#drtodo-init)
  - [`DrToDo list`](#drtodo-list)
  - [`DrToDo ls`](#drtodo-ls)
  - [`DrToDo man`](#drtodo-man)
    - [`DrToDo man all`](#drtodo-man-all)
    - [`DrToDo man config`](#drtodo-man-config)
    - [`DrToDo man md`](#drtodo-man-md)
    - [`DrToDo man mdfiles`](#drtodo-man-mdfiles)
    - [`DrToDo man settings`](#drtodo-man-settings)
  - [`DrToDo show`](#drtodo-show)
  - [`DrToDo undone`](#drtodo-undone)
