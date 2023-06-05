import rich
import rich.markdown
import typer
from importlib import resources
from . import man

from typer_aliases import Typer

from .rich_display import console
from .settings import constants, get_default_config

man_output = None
manapp = Typer()


def md_mdfiles():
    with open(resources.files(man) / 'mdfiles.md', 'r') as f:
        return f.read().format(**constants.__dict__)

def md_config():
    with open(resources.files(man) / 'config.md', 'r') as f:
        return f.read().format(**constants.__dict__, DEFAULT_CONFIG=get_default_config())


@manapp.command()
@manapp.command_alias(name="md")
def mdfiles():
    """
    How Markdown files are used to manage todo items.
    """
    assert man_output
    man_output(md_mdfiles())


@manapp.command()
@manapp.command_alias(name="settings")
def config():
    """
    Where settings are stored and how to configure them.
    """
    assert man_output
    man_output(md_config())


@manapp.command()
def all():
    """List all manual pages"""
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
