import subprocess
import sys
import os
from rich.logging import RichHandler
import logging

logging.basicConfig(level="INFO", datefmt="[%X]", format="%(message)s", handlers=[RichHandler()])
log = logging.getLogger(__name__)


def create_doc_files():
    os.environ["DRTODO_IGNORE_CONFIG"] = "True" # make sure we don't pick up any settings from the user's config file
    log.info("Creating man pages...")
    man = subprocess.run(["poetry", "run", "python", "-m", "drtodo", "man", "--raw", "all"], capture_output=True, text=True)
    help: str = man.stdout

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
