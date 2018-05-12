import sublime_plugin

from . import utils


class GoEventListener(sublime_plugin.EventListener):
    def on_pre_save(self, view):
        if not utils.is_go_view(view):
            return
        view.run_command("go_goimports")
