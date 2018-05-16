import sublime
import sublime_plugin

from . import utils


class GoFormatCommand(sublime_plugin.TextCommand):
    def is_enabled(self):
        return utils.is_go_view(self.view)

    def run(self, edit, cmd):
        view = self.view
        if not utils.is_go_view(view):
            return

        src = view.substr(sublime.Region(0, view.size()))
        filename = view.file_name()

        cmd = [x.format_map({"file": filename}) for x in cmd]
        code, sout, serr = utils.run_go_tool(
            cmd,
            src,
            view,
        )
        if code != 0:
            print("error while running goimports, err: " + serr)
            return

        utils.safe_replace_all(edit, view, src, sout)
