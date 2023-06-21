import subprocess
import sys
import os


def create_doc_files():
    os.environ["DRTODO_IGNORE_CONFIG"] = "True" # make sure we don't pick up any settings from the user's config file
    print("Creating man pages...", file=sys.stderr)
    man = subprocess.run(["poetry", "run", "python", "-m", "drtodo", "man", "--raw", "all"], capture_output=True, text=True)
    help = man.stdout
    print("Creating cli help pages...", file=sys.stderr)
    cli = subprocess.run(["poetry", "run", "typer",
                          "drtodo.main", "utils", "docs", "--name", "DrToDo"],
                          capture_output=True, text=True)
    help += cli.stdout

    # comma separated list of strings to search for in help text
    if "PII_STRINGS" in os.environ:
        print("Scrubbing help text of PII...", file=sys.stderr)
        for pii in os.environ["PII_STRINGS"].split(","):
            # if any of the PII strings are found, replace them with "REDACTED" and print a warning
            if pii in help:
                print(f"WARNING: PII string '{pii}' found!", file=sys.stderr)
                help = help.replace(pii, "REDACTED")
    else:
        print("WARNING: PII_STRINGS not defined, could not verify!", file=sys.stderr)

    print("Creating drtodo/README.md...", file=sys.stderr)
    with open("drtodo/README.md", "w") as f:
        f.write(help)

if __name__ == "__main__":
    create_doc_files()
