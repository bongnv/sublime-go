import json
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


class GoGuruGotoCommand(sublime_plugin.TextCommand):
    def is_enabled(self):
        return utils.is_go_view(self.view)

    def run(self, edit):
        if not utils.is_go_view(self.view):
            return

        filename = self.view.file_name()
        offset = utils.get_byte_offset(self.view)

        code, sout, serr = utils.run_go_tool(
            ["guru", "-json", "-modified", "definition", filename + ":#" + str(offset)],
            stdin=utils.get_file_archive(self.view),
            view=self.view,
        )

        if code != 0:
            print(serr)
            return

        definition = json.loads(sout)
        position = definition['objpos']
        self.view.window().open_file(position, sublime.ENCODED_POSITION)