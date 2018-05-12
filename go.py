import sublime_plugin

from . import gocode
from . import utils


class GoEventListener(sublime_plugin.EventListener):
    def on_query_completions(self, view, prefix, locations):
        if not utils.is_go_view(view):
            return
        return gocode.get_suggestions(view, locations[0])

    def on_pre_save(self, view):
        if not utils.is_go_view(view):
            return
        view.run_command(
            "go_format",
            {
                "cmd": ["goimports", "-e", "-srcdir={file}"],
            },
        )
