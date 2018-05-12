import json
import sublime
import sublime_plugin

from . import utils


class GoGuruGotoCommand(sublime_plugin.TextCommand):
    def is_enabled(self):
        return utils.is_go_view(self.view)

    def run(self, edit):
        if not utils.is_go_view(self.view):
            return

        filename = self.view.file_name()
        offset = utils.get_byte_offset(self.view)

        code, sout, serr = utils.run_go_tool(
            ["guru", "-json", 'definition', filename + ":#" + str(offset)],
            stdin=None,
            file_path=filename,
        )

        if code != 0:
            print(serr)
            return

        definition = json.loads(sout)
        position = definition['objpos']
        self.view.window().open_file(position, sublime.ENCODED_POSITION)
