# DrToDo

**DrToDo, MD**: *a straightforward todo list manager for markdown files in git repos.*

TODO items are listed in markdown (*MD*) files using standard markdown syntax understood by most
environments including Github. You can add and modify these items easily from the command line.
Markdown files are then just committed to git as you'd normally do and shared with others or as
part of projects, or just kept locally in your computer.

## Install

The simplest install is to use `pip`:

```console
$ pip install drtodo
```

This will install todo in whichever python environment you are using. If you are using a virtual env manager like venv, pipenv, poetry, conda
or any other, you can use that to install todo in the environment you want.

> TODO: add instructions for pipx

## Basic Example

Let's go through a simple example on how you might use *DrToDo* straight out of the proverbial box.


```console
# create a new folder to hold your todo items
$ todo init
# add a todo to the global list
$ todo add "clean up folder `pwd`"
  0: 11348e9 ⚫ clean up folder /Users/me/work/src/tmp/p
# list todo items
$ todo list
  0: 11348e9 ⚫ clean up folder /Users/me/work/src/tmp/p
# mark item as done
$ todo done 0
  0: 11348e9 🔘 clean up folder /Users/me/work/src/tmp/p
```

There are many ways to reference todo items, you can use the index number,
the partial hash, the text or a combination of those. For example, all of these
would be equivalent in this example:

```console
$ todo done 11348e9
  0: 11348e9 🔘 clean up folder /Users/me/work/src/tmp/p
$ todo done 'clean up'
  0: 11348e9 🔘 clean up folder /Users/me/work/src/tmp/p
$ todo done --all
  0: 11348e9 🔘 clean up folder /Users/me/work/src/tmp/p
```

There are more options which you can see with `todo --help` or `todo <command> --help`.

Once your items are done you can delete them with `todo clean`:

```console
$ todo clean
~/.drtodo/TODO.md - removing done items:
  0: 11348e9 🔘 clean up folder /Users/me/work/src/tmp/p
```

## Advanced Example

> TODO
>

### use it inside a git repo

> TODO: document this better including the git repo used with `todo init`

