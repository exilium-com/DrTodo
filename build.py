import logging
import os
import subprocess
from urllib.parse import urljoin, urlparse

import mistune
from mistune.renderers.markdown import MarkdownRenderer
from rich.logging import RichHandler

from .drtodo import mdparser

logging.basicConfig(level="INFO", datefmt="[%X]", format="%(message)s", handlers=[RichHandler()])
log = logging.getLogger(__name__)

ABS_DOC_PATH = "https://pypi.org/project/drtodo/"


def create_doc_files():
    os.environ["DRTODO_IGNORE_CONFIG"] = "True" # make sure we don't pick up any settings from the user's config file
    log.info("Creating man pages...")
    man = subprocess.run(["poetry", "run", "python", "-m", "drtodo", "man", "--raw", "all"], capture_output=True, text=True)
    help: str = man.stdout

    # parse markdown using mistune and replace relative links with absolute links
    mistune_parser = mistune.create_markdown(renderer=MarkdownRenderer())
    _, state = mistune_parser.parse(help)

    for link in mdparser.TokenTraverser.tokens_by_type(state.tokens, 'link'):
        if 'attrs' in link and 'url' in link['attrs']:
            # ignore links that are already absolute
            if not urlparse(link['attrs']['url']).netloc:
                absurl = urljoin(ABS_DOC_PATH, link['attrs']['url'])
                log.info(f"'{link['attrs']['url']}' -> {absurl}")
                link['attrs']['url'] = absurl

    # re-render with new links
    help = mistune_parser.render_state(state)  # type: ignore

    log.info("Creating cli help pages...")
    cli = subprocess.run(["poetry", "run", "typer",
                          "drtodo.main", "utils", "docs", "--name", "DrToDo"],
                          capture_output=True, text=True)
    help += cli.stdout

    # comma separated list of strings to search for in help text
    if "PII_STRINGS" in os.environ:
        log.info("Scrubbing help text of PII...")
        for pii in os.environ["PII_STRINGS"].split(","):
            # if any of the PII strings are found, replace them with "REDACTED" and print a warning
            if pii in help:
                log.warning(f"PII string '{pii}' found!")
                help = help.replace(pii, "*REDACTED*")
    else:
        log.warning("PII_STRINGS not defined, could not verify!")

    log.info("Creating drtodo/README.md...")
    with open("drtodo/README.md", "w") as f:
        f.write(help)

if __name__ == "__main__":
    create_doc_files()
