import difflib
import sublime
import sublime_plugin

from . import utils


def diff_sanity_check(a, b):
    if a != b:
        raise Exception("diff sanity check mismatch\n-%s\n+%s" % (a, b))


class GoGoimportsCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        view = self.view
        if not utils.is_go_view(view):
            return

        src = view.substr(sublime.Region(0, view.size()))
        filename = view.file_name()
        code, sout, serr = utils.run_go_tool(
            ["goimports", "-e", "-srcdir=" + filename],
            src,
            filename,
        )
        if code != 0:
            print("error while running goimports, err: " + serr)
            return

        diff = difflib.ndiff(src.splitlines(), sout.splitlines())
        i = 0
        for line in diff:
            if line.startswith("?"):  # skip hint lines
                continue

            l = (len(line) - 2) + 1
            if line.startswith("-"):
                diff_sanity_check(view.substr(
                    sublime.Region(i, i + l - 1)), line[2:])
                view.erase(edit, sublime.Region(i, i + l))
            elif line.startswith("+"):
                view.insert(edit, i, line[2:] + "\n")
                i += l
            else:
                diff_sanity_check(view.substr(
                    sublime.Region(i, i + l - 1)), line[2:])
                i += l
