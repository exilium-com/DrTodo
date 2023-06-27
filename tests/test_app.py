# from typer.testing import CliRunner
import os

os.environ["DRTODO_IGNORE_CONFIG"] = "True"
# ensures consistent behavior regardless of local config files
# NOTE: this means that config loading is not effectively tested here

from drtodo import __version__       # noqa: E402
from drtodo.main import app          # noqa: E402
from typer_aliases import CliRunner  # noqa: E402


runner = CliRunner(mix_stderr=False)


def test_help():
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    assert "Usage:" in result.stdout


def test_debug():
    result = runner.invoke(app, ["debug"])
    assert result.exit_code == 0
    assert "'appname': 'DrToDo'" in result.stdout


def test_list():
    result = runner.invoke(app, ["list"])
    assert result.exit_code == 0
    assert "make it useful" in result.stdout
    assert "bug 2" in result.stdout
    # output is of the form "id: hash bullet make it useful"
    # extract id and hash from the output
    pos = result.stdout.find('make it useful')
    assert pos > 0
    colon = result.stdout[:pos].rfind(':')
    assert colon > 0 and result.stdout[colon] == ':'
    hash = result.stdout[colon + 2: colon + 9].strip()
    index = result.stdout[colon-3:colon].strip()

    # list using various arguments to show subsets of items, check hash and id
    result = runner.invoke(app, ["list", index])
    assert result.exit_code == 0
    assert "make it useful" in result.stdout
    assert "bug" not in result.stdout

    result = runner.invoke(app, ["list", hash])
    assert result.exit_code == 0
    assert "make it useful" in result.stdout
    assert "bug" not in result.stdout

    result = runner.invoke(app, ["list", "useful"])
    assert result.exit_code == 0
    assert "make it useful" in result.stdout
    assert "bug" not in result.stdout

    result = runner.invoke(app, ["list", "--id", hash])
    assert result.exit_code == 0
    assert "make it useful" in result.stdout
    assert "bug" not in result.stdout

    result = runner.invoke(app, ["list", "--range", f"{index}::1000"])
    assert result.exit_code == 0
    assert "make it useful" in result.stdout
    assert "bug" not in result.stdout

    result = runner.invoke(app, ["list", "2:4"])
    assert result.exit_code == 0
    assert "useful" not in result.stdout
    assert "bug 1" in result.stdout
    assert "bug 2" in result.stdout


def test_section():
    result = runner.invoke(app, ['--section', '', 'list'])
    assert result.exit_code == 0
    assert len(result.stdout.splitlines()) == 5  # 2 lists with 2 items each plus header

    result = runner.invoke(app, ['--section', '## TODO', 'list'])
    assert result.exit_code == 0
    assert len(result.stdout.splitlines()) == 3  # 2 items plus header


def test_show():
    result = runner.invoke(app, ['show'])
    assert result.exit_code == 0
    assert "ice cream" in result.stdout
    assert '##' not in result.stdout


def test_version():
    result = runner.invoke(app, ["--version"])
    assert result.exit_code == 0
    assert "DrToDo" in result.stdout
    assert __version__ in result.stdout


def test_remove():
    result = runner.invoke(app, ["remove", "1"])
    assert result.exit_code == 0
    assert "bug" not in result.stdout

    result = runner.invoke(app, ["ls"])
    assert result.exit_code == 0
    assert "make it useful" not in result.stdout

    # restore the backup so we can run the tests again
    result = runner.invoke(app, ["backup", "--force", "restore"])
    assert result.exit_code == 0
    assert "restored:" in result.stdout


def test_add_remove():
    result = runner.invoke(app, ["add", "testing added item"])
    # output is of the form "id: hash bullet testing added item"
    assert result.exit_code == 0
    assert "testing added item" in result.stdout
    # extract id and hash from the output
    colon = result.stdout.find(":")
    assert colon > 0
    hash = result.stdout[colon + 2: colon + 9].strip()
    id = result.stdout[colon-3:colon].strip()

    result = runner.invoke(app, ["list"])
    # output is the same form but with many lines now, so we need to find the line with the hash
    assert result.exit_code == 0
    assert "testing added item" in result.stdout
    assert hash in result.stdout
    assert id in result.stdout

    # now delete the item
    result = runner.invoke(app, ["remove", id])
    assert result.exit_code == 0

    # ensure that the item is gone
    result = runner.invoke(app, ["list"])
    assert result.exit_code == 0
    assert "testing added item" not in result.stdout
    assert hash not in result.stdout
    # id may be reused so we can't check for it


def test_do_done():
    result = runner.invoke(app, ["add", "testing added item"])
    # output is of the form "id: hash bullet testing added item"
    assert result.exit_code == 0
    assert "testing added item" in result.stdout
    # extract id and hash from the output
    colon = result.stdout.find(":")
    assert colon > 0
    hash = result.stdout[colon + 2: colon + 9].strip()
    id = result.stdout[colon-3:colon].strip()

    result = runner.invoke(app, ["list"])
    # output is the same form but with many lines now, so we need to find the line with the hash
    assert result.exit_code == 0
    assert "testing added item" in result.stdout
    assert hash in result.stdout
    assert id in result.stdout

    # now mark this item as done and check that it is done
    result = runner.invoke(app, ["done", id])
    assert result.exit_code == 0
    assert "testing added item" in result.stdout
    assert hash in result.stdout
    assert id in result.stdout

    result = runner.invoke(app, ["list"])
    assert result.exit_code == 0
    assert "testing added item" in result.stdout
    assert hash in result.stdout
    assert id in result.stdout
    # TODO: validate that the item is marked as done, depends on the output format

    # now mark this item as not done and check that it is not done
    result = runner.invoke(app, ["undone", id])
    assert result.exit_code == 0
    assert "testing added item" in result.stdout
    assert hash in result.stdout
    assert id in result.stdout

    result = runner.invoke(app, ["list"])
    assert result.exit_code == 0
    assert "testing added item" in result.stdout
    assert hash in result.stdout
    assert id in result.stdout
    # TODO: validate that the item is marked as done, depends on the output format

    # now delete the item
    result = runner.invoke(app, ["remove", id])
    assert result.exit_code == 0

    # ensure that the item is gone
    result = runner.invoke(app, ["list"])
    assert result.exit_code == 0
    assert "testing added item" not in result.stdout
    assert hash not in result.stdout
    # id may be reused so we can't check for it


def test_man():
    result = runner.invoke(app, ["man", "--raw", "all"])
    assert result.exit_code == 0
    assert "# Markdown Files" in result.stdout
    assert "# Settings" in result.stdout


def test_aliases():
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    assert result.stdout.find("ls") > 0

    result = runner.invoke(app, ["ls"])
    assert result.exit_code == 0
    assert "make it useful" in result.stdout

    result = runner.invoke(app, ["man"])
    assert result.exit_code == 0
    assert result.stdout.find("settings") > 0 # settings is a command alias
