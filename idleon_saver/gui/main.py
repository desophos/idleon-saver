from argparse import Namespace
from pathlib import Path

from kivy.app import App
from kivy.factory import Factory
from kivy.properties import ListProperty, ObjectProperty, StringProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.popup import Popup
from kivy.uix.screenmanager import Screen, ScreenManager
from scripts import inject, stencyl2json


class FileChooserDialog(BoxLayout):
    filters = ListProperty([])
    done = ObjectProperty(None)
    cancel = ObjectProperty(None)


class PathWindow(Screen):
    back = ObjectProperty(None)
    next = ObjectProperty(None)
    action = ObjectProperty(None)
    caption = StringProperty("")
    default_path = StringProperty("")
    path_input = ObjectProperty(None)
    path_filters = ListProperty([])
    error = ObjectProperty(None)

    def __init__(self, caption, default_path, path_filters, **kwargs):
        super().__init__(**kwargs)
        self.caption = caption
        self.default_path = default_path
        self.on_path_text(default_path)
        self.path_filters = path_filters

    def dismiss_popup(self):
        self._popup.dismiss()

    def show_filebrowser(self):
        content = FileChooserDialog(
            done=self.set_path, cancel=self.dismiss_popup, filters=self.path_filters
        )
        self._popup = Popup(title="Find file", content=content, size_hint=(0.9, 0.9))
        self._popup.open()

    def set_path(self, directory, filename):
        try:
            self.path_input.text = str(Path(directory, filename[0]))
        except IndexError:
            pass  # no file selected, so just treat it like canceling
        self.dismiss_popup()

    def on_path_text(self, text):
        if not Path(text).exists():
            self.error.text = "Invalid path!"
            self.next.disabled = True
        else:
            self.error.text = ""
            self.next.disabled = False


class MainWindow(ScreenManager):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        screens = [
            PathWindow(
                "Path to LegendsOfIdleon.exe:",
                "C:/Program Files (x86)/Steam/steamapps/common/Legends of Idleon/LegendsOfIdleon.exe",
                ["*.exe"],
                name="find_exe",
                action=lambda path: inject.main(Path(path)),
            ),
            PathWindow(
                "Path to idleonsave.txt:",
                str(Path.home() / "Downloads/idleonsave.txt"),
                ["*.txt"],
                name="find_save",
                action=lambda path: stencyl2json.main(Namespace(workdir=Path(path))),
            ),
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


class Saver(App):
    def build(self):
        return MainWindow()


Factory.register("PathWindow", cls=PathWindow)
Factory.register("FileChooserDialog", cls=FileChooserDialog)


if __name__ == "__main__":
    Saver().run()
