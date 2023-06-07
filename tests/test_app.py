# from typer.testing import CliRunner
from typer_aliases import CliRunner

from drtodo.main import app
from drtodo import __version__


runner = CliRunner()


def test_help():
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    assert "Usage:" in result.stdout


def test_debug():
    result = runner.invoke(app, ["debug"])
    assert result.exit_code == 0
    assert "'appname': 'DrTodo'" in result.stdout


def test_list():
    result = runner.invoke(app, ["list"])
    assert result.exit_code == 0
    assert "make it useful" in result.stdout
    assert "bug 2" in result.stdout


def test_section():
    result = runner.invoke(app, ['--section', '', 'list'])
    assert result.exit_code == 0
    assert len(result.stdout.splitlines()) == 5  # 2 lists with 2 items each plus header

    result = runner.invoke(app, ['--section', '## TODO', 'list'])
    assert result.exit_code == 0
    assert len(result.stdout.splitlines()) == 3  # 2 items plus header


def test_version():
    result = runner.invoke(app, ["--version"])
    assert result.exit_code == 0
    assert "DrTodo" in result.stdout
    assert __version__ in result.stdout


def test_add_do_done_remove():
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

    # TODO: this command does not exist yet
    # # now delete the item
    # result = runner.invoke(app, ["remove", id])

    # # ensure that the item is gone
    # result = runner.invoke(app, ["list"])
    # assert result.exit_code == 0
    # assert "testing added item" not in result.stdout
    # assert hash not in result.stdout
    # # id may be reused so we can't check for it


# TODO: this test fails with invalid options but running it without invoke() works fine
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
