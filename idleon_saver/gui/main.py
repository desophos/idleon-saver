import logging
import os
import sys
from multiprocessing import freeze_support
from enum import Enum
from pathlib import Path
from zipfile import ZipFile

from idleon_saver.utility import BUGREPORT_LINK, logs_dir, user_dir

# Set log config before all kivy imports
# to ensure that *all* kivy logging obeys our settings.
# (Prevents kivy.config from creating extra log files.)
os.environ["KCFG_KIVY_LOG_DIR"] = str(logs_dir())
os.environ["KCFG_KIVY_LOG_NAME"] = "log_%y-%m-%d_%_.txt"
os.environ["KCFG_KIVY_LOG_LEVEL"] = "info"
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
from kivy.properties import ListProperty, ObjectProperty, StringProperty
from kivy.resources import resource_add_path, resource_find
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.popup import Popup
from kivy.uix.screenmanager import Screen, ScreenManager

# Make other modules use Kivy's logger.
logging.Logger.manager.root = Logger

from scripts import inject
from scripts.decode import read_stencyl
from scripts.export import save_idleon_companion, to_idleon_companion


class VBox(BoxLayout):
    pass


class ErrorDialog(VBox):
    done = ObjectProperty(None)

    def open_logs(self):
        with ZipFile(user_dir() / "logs.zip", "w") as zf:
            for f in logs_dir().iterdir():
                zf.write(f, f.name)
        os.startfile(user_dir(), "explore")

    def open_github(self):
        os.startfile(BUGREPORT_LINK)


class FileChooserDialog(VBox):
    filters = ListProperty([])
    done = ObjectProperty(None)
    cancel = ObjectProperty(None)


class StartScreen(Screen):
    pass


class EndScreen(Screen):
    pass


Blockers = Enum("Blockers", "PATH ACTION")


class PathScreen(Screen):
    back = ObjectProperty(None)
    next = ObjectProperty(None)
    action = ObjectProperty(None)
    caption = StringProperty("")
    default_path = StringProperty("")
    path_input = ObjectProperty(None)
    path_filters = ListProperty([])
    error = ObjectProperty(None)
    instructions = StringProperty("")

    blockers = dict.fromkeys(list(Blockers), False)

    def __init__(self, caption, default_path, path_filters, instructions="", **kwargs):
        super().__init__(**kwargs)
        self.caption = caption
        self.default_path = default_path
        self.on_path_text(default_path)
        self.path_filters = path_filters
        self.instructions = instructions

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

    def dismiss_popup(self):
        self._popup.dismiss()

    def show_filebrowser(self):
        content = FileChooserDialog(
            done=self.set_path, cancel=self.dismiss_popup, filters=self.path_filters
        )
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

        if not Path(text).exists():
            self.error.opacity = 1.0
            self.block_next(Blockers.PATH, True)
        else:
            self.error.opacity = 0.0
            self.block_next(Blockers.PATH, False)

    def try_action(self, path):
        try:
            self.action(path)
        except Exception as e:
            Logger.exception(e)
            content = ErrorDialog(done=self.dismiss_popup)
            self._popup = Popup(title="Error :(", content=content, size_hint=(0.9, 0.9))
            self._popup.open()
        else:
            self.manager.transition.direction = "left"
            self.manager.current = self.manager.next()


class MainWindow(ScreenManager):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        def convert_save(path: str):
            infile = Path(path)
            save_idleon_companion(
                infile.parent,
                to_idleon_companion(read_stencyl(infile.parent, infile.name).unwrapped),
            )

        screens = [
            StartScreen(name="start"),
            PathScreen(
                "Path to LegendsOfIdleon.exe:",
                "C:/Program Files (x86)/Steam/steamapps/common/Legends of Idleon/LegendsOfIdleon.exe",
                ["*.exe"],
                "Make sure Steam is running, then click Next to open Legends of Idleon.\nYou'll be prompted to download your save file, then you can close the game.",
                name="find_exe",
                action=lambda path: inject.main(Path(path)),
            ),
            PathScreen(
                "Path to idleonsave.txt:",
                str(Path.home().joinpath("Downloads", "idleonsave.txt")),
                ["*.txt"],
                "Click Next to convert the save file you downloaded into a format ready to import into Idleon Companion.",
                name="find_save",
                action=convert_save,
            ),
            EndScreen(name="end"),
        ]

        for screen in screens:
            self.add_widget(screen)

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
        self.title = "Idleon Saver"
        return MainWindow()


if __name__ == "__main__":
    # Support multiprocessing in frozen bundle.
    freeze_support()

    # Add data dir to Kivy path in frozen bundle.
    if hasattr(sys, "_MEIPASS"):
        resource_add_path(os.path.join(sys._MEIPASS))  # type: ignore[attr-defined]

    IdleonSaver(kv_file="main.kv").run()
