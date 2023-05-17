from typer.testing import CliRunner

from drtodo.main import app
from drtodo import __version__

runner = CliRunner()


def test_help():
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    assert "Usage:" in result.stdout


def test_debug():
    result = runner.invoke(app, ["--debug"])
    assert result.exit_code == 0
    assert "Usage:" in result.stdout


def test_list():
    result = runner.invoke(app, ["list"])
    assert result.exit_code == 0
    assert "make it useful" in result.stdout
    assert "bug 2" in result.stdout


def test_version():
    result = runner.invoke(app, ["--version"])
    assert result.exit_code == 0
    assert "DrTodo" in result.stdout
    assert __version__ in result.stdout


def test_man():
    result = runner.invoke(app, ["man --raw all"])
    assert result.exit_code == 0
    assert "# Markdown Files" in result.stdout
    assert "# Settings" in result.stdout
