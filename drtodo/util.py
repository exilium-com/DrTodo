import rich
import rich.markdown
from .rich_display import console

def print_md_as_raw(mdstring: str):
    console().print(mdstring, markup=False, highlight=False)

def print_md_pretty(mdstring: str):
    console().print(rich.markdown.Markdown(mdstring))
