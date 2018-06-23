import sublime_plugin
import sublime
from SublimeLinter.lint import util, Linter

from .libs import cmds
from .libs import events
from .libs import linters


class _API:
    ENCODED_POSITION = sublime.ENCODED_POSITION
    STREAM_STDERR = util.STREAM_STDERR
    STREAM_STDOUT = util.STREAM_STDOUT

    @classmethod
    def new_region(cls, a, b):
        return sublime.Region(a, b)

    @classmethod
    def set_timeout(cls, fn, duration):
        return sublime.set_timeout(fn, duration)

    @classmethod
    def active_window(cls, active_window):
        return sublime.active_window()


class GoFormatCommand(cmds.GoFormatCommand, sublime_plugin.TextCommand, _API):
    pass


class GoGuruGotoCommand(cmds.GoGuruGotoCommand, sublime_plugin.TextCommand, _API):
    pass


class GoFindReferencesCommand(cmds.GoFindReferencesCommand, sublime_plugin.TextCommand, _API):
    pass


class GoBuildCommand(cmds.GoBuildCommand, sublime_plugin.WindowCommand, _API):
    pass


class GoEventListener(events.GoEventListener, sublime_plugin.EventListener, _API):
    pass


class Gotype(linters.Gotype, Linter, _API):
    def __init__(self, view, settings):
        linters.Gotype.__init__(self)
        Linter.__init__(self, view, settings)


class Golint(linters.Golint, Linter, _API):
    def __init__(self, view, settings):
        linters.Golint.__init__(self)
        Linter.__init__(self, view, settings)


class Govet(linters.Govet, Linter, _API):
    def __init__(self, view, settings):
        linters.Govet.__init__(self)
        Linter.__init__(self, view, settings)


class Megacheck(linters.Megacheck, Linter, _API):
    def __init__(self, view, settings):
        linters.Megacheck.__init__(self)
        Linter.__init__(self, view, settings)
