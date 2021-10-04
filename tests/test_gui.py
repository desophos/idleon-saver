import sys

import pytest
from idleon_saver.utility import wait_for
from telenium.context import TeleniumContext

path_input = "//PathScreen//TextInput"
# telenium loads attribute selector values as json.
# We can't select by the fmt attribute because it's Formats,
# which is an enum and therefore can't be serialized to json.
export_ic = "//EndScreen//ExportButtonBox[0]/Button"
export_cog = "//EndScreen//ExportButtonBox[1]/Button"


def current_screen(app: TeleniumContext) -> str:
    return app.cli.evaluate("window.current_screen.__class__.__name__")


def back_button(app: TeleniumContext) -> str:
    return f"//{current_screen(app)}//BackButton"


def next_button(app: TeleniumContext) -> str:
    return f"//{current_screen(app)}//NextButton"


def next_blocked(app: TeleniumContext):
    return app.cli.getattr(next_button(app), "disabled")


@pytest.fixture
def app(tmp_path, stencylsave) -> TeleniumContext:
    with TeleniumContext(
        cmd_process=[sys.executable, "-m", "telenium.execute"],
        cmd_entrypoint=["idleon_saver/gui/main.py"],
    ) as ctx:
        ctx.cli.select_and_store("window", "/MainWindow")
        ctx.cli.execute(f'window.get_stencyl = lambda _: r"{stencylsave}"')
        ctx.cli.execute(
            f"""
            from pathlib import Path
            window.userdir = Path(r"{tmp_path}")
            """
        )
        yield ctx


@pytest.fixture
def mock_path(tmp_path):
    def f(name):
        p = tmp_path / name
        p.touch()
        return p

    return f


@pytest.fixture
def app_at_pathscreen(app, mock_path) -> TeleniumContext:
    app.cli.wait_click(next_button(app))
    assert app.cli.wait("//PathScreen", timeout=5)
    app.cli.setattr(path_input, "text", str(mock_path("LegendsOfIdleon.exe")))
    app.cli.select_and_store("path_screen", "//PathScreen")
    return app


@pytest.fixture
def app_at_endscreen(app_at_pathscreen) -> TeleniumContext:
    app = app_at_pathscreen
    app.cli.wait_click(next_button(app))
    assert app.cli.wait("//EndScreen", timeout=5)
    return app


def test_smoke(app):
    assert app


def test_start_next(app):
    app.cli.wait_click(next_button(app))
    assert "PathScreen" == current_screen(app)


@pytest.mark.parametrize(
    "blocked,text",
    [
        (True, ""),
        (True, "!@#$%^&*()_+"),
        (True, "~"),
    ],
)
def test_path(app, blocked, text):
    app.cli.wait_click(next_button(app))
    app.cli.setattr(path_input, "text", text)
    assert blocked == next_blocked(app)


@pytest.mark.parametrize(
    "blocked,text",
    [
        (True, "_.txt"),
        (False, "LegendsOfIdleon.exe"),
    ],
)
def test_file_path(app, mock_path, blocked, text):
    test_path(app, blocked, str(mock_path(text)))


def test_path_next(app_at_pathscreen):
    app = app_at_pathscreen
    app.cli.wait_click(next_button(app))
    assert wait_for(lambda: "EndScreen" == current_screen(app), 5.0)


def test_file_saved(app_at_pathscreen, tmp_path):
    app = app_at_pathscreen
    app.cli.wait_click(next_button(app))
    assert wait_for((tmp_path / "idleon_save.json").exists, 5.0)


def test_loading(app_at_pathscreen):
    app = app_at_pathscreen
    # Fake loading time.
    # Can't use setattr because functions are not JSON-serializable.
    app.cli.execute("from time import sleep; path_screen.action = lambda _: sleep(10)")
    app.cli.wait_click(next_button(app))
    # Next button should be unclickable.
    assert next_blocked(app)
    # Progress bar should be visible and filling.
    assert 0.0 < app.cli.getattr("//ProgressBar", "opacity")
    assert 0 < app.cli.getattr("//ProgressBar", "value")
    # Wait for action to finish. Progress bar should disappear.
    app.assertNotExists("//ProgressBar", timeout=10)
    # We should be on the end screen now.
    assert "EndScreen" == current_screen(app)


@pytest.mark.parametrize(
    "button,files",
    [
        (export_ic, ["idleon_companion.json"]),
        (export_cog, ["cog_datas.csv", "empties_datas.csv"]),
    ],
)
def test_export(app_at_endscreen, tmp_path, button, files):
    app = app_at_endscreen
    app.cli.wait_click(button)
    for f in files:
        assert wait_for((tmp_path / f).exists, 5.0)
