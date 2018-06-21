import sublime


class Command:
    ENCODED_POSITION = sublime.ENCODED_POSITION

    def __init__(self, view=None, window=None, edit=None):
        self.view, self.window = _get_view_window(view, window)
        self.edit = edit

    def new_region(cls, a, b):
        return sublime.Region(a, b)

    def set_timeout(cls, fn, duration):
        return sublime.set_timeout(cls, fn, duration)

    def active_window(cls, active_window):
        return sublime.active_window()


def _get_view_window(cls, view=None, window=None):
    if view is not None and not isinstance(view, sublime.View):
        raise TypeError("view must be an instance of sublime.View")

    if window is not None and not isinstance(window, sublime.Window):
        raise TypeError("window must be an instance of sublime.Window")

    if view and window is None:
        return view, view.window()
    if window is None:
        window = sublime.active_window()
    if view is None and window:
        return window.active_view(), window
    return view, window
