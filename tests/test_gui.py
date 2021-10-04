import json
import sys

import pytest
from telenium.context import TeleniumContext

path_input = "//PathScreen//TextInput"


def current_screen(app: TeleniumContext) -> str:
    return app.cli.evaluate("window.current_screen.__class__.__name__")


def back_button(app: TeleniumContext) -> str:
    return f"//{current_screen(app)}//BackButton"


def next_button(app: TeleniumContext) -> str:
    return f"//{current_screen(app)}//NextButton"


def next_blocked(app: TeleniumContext):
    return app.cli.getattr(next_button(app), "disabled")


@pytest.fixture
def app():
    with TeleniumContext(
        cmd_process=[sys.executable, "-m", "telenium.execute"],
        cmd_entrypoint=["idleon_saver/gui/main.py"],
    ) as ctx:
        ctx.cli.select_and_store("window", "/MainWindow")
        yield ctx


@pytest.fixture
def mock_path(tmp_path):
    def f(name):
        p = tmp_path / name
        p.touch()
        return p

    return f


@pytest.fixture
def app_at_pathscreen(app, mock_path, tmp_path, jsonsave):
    app.cli.wait_click(next_button(app))
    app.cli.setattr(path_input, "text", str(mock_path("LegendsOfIdleon.exe")))
    # We need to jump through hoops to mock the inject action
    # because functions aren't JSON-serializable.
    app.cli.select_and_store("path_screen", "//PathScreen")
    app.cli.execute(
        f"""
        import json
        from pathlib import Path
        from scripts.export import save_idleon_companion, to_idleon_companion
        path_screen.action = lambda _: save_idleon_companion(
            Path(r"{tmp_path}"),
            to_idleon_companion(
                json.loads('{json.dumps(jsonsave)}')
            )
        )
        """
    )
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
    assert "EndScreen" == current_screen(app)


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
    app.assertNotExists("//ProgressBar", timeout=5)
    # We should be on the end screen now.
    assert "EndScreen" == current_screen(app)
