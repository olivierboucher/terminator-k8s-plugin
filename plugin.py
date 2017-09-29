import yaml

from threading import Timer
from os.path import expanduser

from gi.repository import Gtk

from terminatorlib.plugin import Plugin
from terminatorlib.terminator import Terminator
from terminatorlib.translation import _

from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

AVAILABLE = ['K8sPlugin']

HOME = expanduser('~')
KUBEDIR = HOME + '/.kube'
KUBECONFIG = KUBEDIR + '/config'

class K8sConfigEventHandler(FileSystemEventHandler):
    terminal = None
    first = True

    def __init__(self):
        FileSystemEventHandler.__init__(self)
        t = Timer(1.0, self.set_console_title)
        t.start()

    def on_modified(self, event):
        if event.src_path == KUBECONFIG:
            self.set_console_title()

    def set_console_title(self):
        kubeConfig = self.get_kube_config()

        terminator = Terminator()
        if self.first:
            self.first = False
            for terminal in terminator.terminals:
                terminal.titlebar.set_custom_string(kubeConfig['current-context'])
        else:
            for terminal in terminator.terminals:
                terminal.titlebar.label.set_text(kubeConfig['current-context'], force=True)

    def get_kube_config(self):
        with open(KUBECONFIG, 'r') as stream:
            return yaml.load(stream)


class K8sPlugin(Plugin):
    capabilities = []
    observer = None

    def __init__(self):
        Plugin.__init__(self)
        event_handler = K8sConfigEventHandler()

        self.observer = Observer()
        self.observer.schedule(event_handler, KUBEDIR, recursive=False)
        self.observer.start()

    def unload(self):
        if self.observer is not None:
            self.observer.stop()
            self.observer.join()
