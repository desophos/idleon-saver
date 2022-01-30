import json
import logging
import os
import sys
import threading
from enum import Enum
from pathlib import Path
from time import sleep
from zipfile import ZipFile

from idleon_saver.utility import BUGREPORT_LINK, logs_dir, user_dir

# Set log config before all kivy imports
# to ensure that *all* kivy logging obeys our settings.
# (Prevents kivy.config from creating extra log files.)
os.environ["KCFG_KIVY_LOG_DIR"] = str(logs_dir())
os.environ["KCFG_KIVY_LOG_NAME"] = "log_%y-%m-%d_%_.txt"
os.environ["KCFG_KIVY_LOG_LEVEL"] = "debug"
os.environ["KCFG_KIVY_LOG_MAXFILES"] = "10"

from kivy.config import Config

# We need to change kivy config before other kivy imports.
Config.set("graphics", "width", 820)
Config.set("graphics", "minimum_width", 700)
Config.set("graphics", "height", 300)
Config.set("graphics", "minimum_height", 300)
Config.set("input", "mouse", "mouse,disable_multitouch")

from kivy.app import App
from kivy.clock import Clock
from kivy.logger import Logger
from kivy.properties import ListProperty, ObjectProperty, OptionProperty, StringProperty
from kivy.resources import resource_add_path
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.popup import Popup
from kivy.uix.screenmanager import Screen, ScreenManager

# Make other modules use Kivy's logger.
logging.Logger.manager.root = Logger

from idleon_saver.scripts import inject
from idleon_saver.scripts.export import FirebaseExporter
from idleon_saver.utility import Formats, friendly_name


class ButtonBox(BoxLayout):
    pass


class ExportButtonBox(ButtonBox):
    button = ObjectProperty(None)
    label = ObjectProperty(None)
    fmt = OptionProperty(Formats.IC, options=list(Formats))
    try_export = ObjectProperty(None)

    def on_kv_post(self, _):
        self.label.text = f"to {friendly_name(self.fmt.value)}"
        self.button.bind(on_release=self.btn_released)

    def btn_released(self, instance):
        if self.try_export(self.fmt):
            instance.text = "Exported"


class VBox(BoxLayout):
    pass


class ErrorDialog(VBox):
    text = StringProperty("")
    done = ObjectProperty(None)

    @staticmethod
    def open_logs():
        with ZipFile(user_dir() / "logs.zip", "w") as zf:
            for f in user_dir().rglob("*.*"):
                # Include all data files
                if f.suffix != ".zip":
                    zf.write(f, f.name)
        # skipcq: BAN-B606
        os.startfile(user_dir(), "explore")

    @staticmethod
    def open_github():
        # skipcq: BAN-B606
        os.startfile(BUGREPORT_LINK)


class FileChooserDialog(VBox):
    filters = ListProperty([])
    done = ObjectProperty(None)
    cancel = ObjectProperty(None)


class MyScreen(Screen):
    def dismiss_popup(self):
        try:
            self._popup.dismiss()
        except AttributeError as e:
            Logger.exception("Popup dismissed before being created", exc_info=e)

    def popup_error(self, text):
        content = ErrorDialog(text=text, done=self.dismiss_popup)
        # skipcq: PYL-W0201
        self._popup = Popup(title="Error :(", content=content, size_hint=(0.95, 0.95))
        self._popup.open()


class StartScreen(MyScreen):
    pass


class EndScreen(MyScreen):
    export = ObjectProperty(None)

    def try_export(self, fmt: Formats):
        try:
            self.export(fmt)
        # skipcq: PYL-W0703
        except Exception as e:
            Logger.exception(e)
            self.popup_error(
                text=(
                    "Oops! Something went wrong.\n\n"
                    "If you keep getting this error, "
                    "please report it on GitHub with "
                    "your logs.zip and idleon_save.json attached."
                )
            )
            return False
        else:
            return True


Blockers = Enum("Blockers", "PATH ACTION")


class PathScreen(MyScreen):
    back = ObjectProperty(None)
    next = ObjectProperty(None)
    action = ObjectProperty(None)
    caption = StringProperty("")
    default_path = StringProperty("")
    path_input = ObjectProperty(None)
    path_filters = ListProperty([])
    error = ObjectProperty(None)
    instructions = StringProperty("")
    progress = ObjectProperty(None)

    blockers = dict.fromkeys(list(Blockers), False)
    action_done = threading.Event()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.on_path_text(self.default_path)
        # Recheck path every second in case of filesystem changes.
        # Hopefully not a performance issue.
        Clock.schedule_interval(lambda dt: self.on_path_text(), 1)

    def block_next(self, which: Blockers, val: bool):
        """Disable "Next" button if blocked for any reason.

        Enable when all blocks are cleared.
        True means "blocked" to match Button.disabled.
        """
        self.blockers[which] = val
        self.next.disabled = any(self.blockers.values())

    def show_filebrowser(self):
        content = FileChooserDialog(
            done=self.set_path, cancel=self.dismiss_popup, filters=self.path_filters
        )
        # skipcq: PYL-W0201
        self._popup = Popup(title="Find file", content=content, size_hint=(1, 1))
        self._popup.open()

    def set_path(self, directory, filename):
        try:
            self.path_input.text = str(Path(directory, filename[0]))
        except IndexError:
            pass  # no file selected, so just treat it like canceling
        self.dismiss_popup()

    def on_path_text(self, text=None):
        if text is None:
            text = self.path_input.text

        if text and Path(text).exists() and Path(text).name == "LegendsOfIdleon.exe":
            # Valid path -> allow next
            self.error.opacity = 0.0
            self.block_next(Blockers.PATH, False)
        else:
            # Invalid path -> block next
            self.error.opacity = 1.0
            self.block_next(Blockers.PATH, True)

    def increment_progress(self, amt: int, slp: float):
        """Increments progress until self.action_done is set.

        Args:
            amt: Amount to increment progress bar by.
            slp: Seconds to sleep in between increments.

        Time to fill progress bar = 100 * slp / amt.
        """
        self.progress.opacity = 1.0

        while not self.action_done.is_set():
            self.progress.value += amt
            sleep(slp)

        # Reset progress bar.
        self.progress.opacity = 0.0
        self.progress.value = 0

    def resolve_action(self, path):
        # Increment progress bar while action is underway.
        self.action_done.clear()
        threading.Thread(target=self.increment_progress, args=(1, 0.3)).start()

        try:
            self.action(path)
        # skipcq: PYL-W0703
        except Exception as e:
            Logger.exception(e)
            self.popup_error(
                text=(
                    "Oops! Something went wrong. "
                    "Make sure Steam is running and Legends of Idleon is closed, "
                    "then check the path and try again. "
                    "If it still doesn't work, "
                    "make sure you've played a character recently.\n\n"
                    "If you keep getting this error, "
                    "please report it on GitHub with your logs.zip attached."
                )
            )
        else:
            self.manager.transition.direction = "left"
            self.manager.current = self.manager.next()
        finally:
            self.action_done.set()
            # Only re-enable "Next" button once action is completed.
            self.next.text = "Next"
            self.block_next(Blockers.ACTION, False)

    def start_action(self, path):
        # Disable "Next" button until action is completed.
        self.next.text = "Loading..."
        self.block_next(Blockers.ACTION, True)

        # Use threading to avoid freezing the UI.
        threading.Thread(target=self.resolve_action, args=(path,)).start()


class MainWindow(ScreenManager):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.savedata = None
        self.userdir = user_dir()

        screens = [
            StartScreen(name="start"),
            PathScreen(
                caption="Path to LegendsOfIdleon.exe:",
                default_path="C:/Program Files (x86)/Steam/steamapps/common/Legends of Idleon/LegendsOfIdleon.exe",
                path_filters=["*.exe"],
                instructions="Make sure Steam is running and Legends of Idleon is closed, then click Next.\nLegends of Idleon will open briefly to retrieve your save data.",
                name="find_exe",
                action=self.get_json,
            ),
            EndScreen(name="end", export=self.export),
        ]

        for screen in screens:
            self.add_widget(screen)

    @staticmethod
    def download_savedata(path: str) -> dict:
        return inject.main(Path(path))

    def get_json(self, path: str):
        self.savedata = self.download_savedata(path)
        with open(self.userdir / "idleon_save.json", "w", encoding="utf-8") as file:
            json.dump(self.savedata, file)

    def export(self, fmt: Formats):
        FirebaseExporter(self.savedata).export(fmt, self.userdir)

    def next(self):
        # don't wrap from last to first screen
        if self.current == self.screen_names[-1]:
            return self.current
        else:
            return super().next()

    def previous(self):
        # don't wrap from first to last screen
        if self.current == self.screen_names[0]:
            return self.current
        else:
            return super().previous()


class IdleonSaver(App):
    def build(self):
        # skipcq: PYL-W0201
        self.title = "Idleon Saver"
        return MainWindow()


if __name__ == "__main__":
    import importlib.metadata

    # Add data dir to Kivy path in frozen bundle.
    if hasattr(sys, "_MEIPASS"):
        # skipcq: PYL-W0212
        resource_add_path(os.path.join(sys._MEIPASS))  # type: ignore[attr-defined]

    Logger.info(f"Idleon Saver: version {importlib.metadata.version('idleon_saver')}")
    IdleonSaver(kv_file="main.kv").run()
