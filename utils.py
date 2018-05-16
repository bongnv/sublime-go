import difflib
import os
import sys
import sublime
import subprocess
import shellenv


_platform = {
    'win32': 'windows',
    'darwin': 'osx'
}.get(sys.platform, 'linux')


# is_go_view return true/false whether the given view is for a go source code or not.
def is_go_view(view):
    return view.match_selector(0, "source.go")


def executable_path(cmd, view=None, window=None):
    for dir_ in prepare_env(view, window).get("PATH", "").split(os.pathsep):
        p = os.path.join(dir_, cmd)
        if _check_executable(p):
            return p
    return cmd


def prepare_env(view=None, window=None):
    gopath = _get_gopath(view, window)
    goroot = _get_goroot(view, window)

    _, my_env = shellenv.get_env()
    paths = [my_env["PATH"]]
    if len(gopath) > 0:
        paths.append(os.path.join(gopath, "bin"))
        my_env["GOPATH"] = gopath

    if len(goroot) > 0:
        paths.append(os.path.join(goroot, "bin"))
        my_env["GOROOT"] = goroot

    my_env["PATH"] = os.pathsep.join(paths)
    return my_env


# run_go_tool executes a go tool command and return code, stdout, stderr.
def run_go_tool(cmd, stdin=None, view=None, window=None):
    stdin_p = subprocess.PIPE
    if stdin is None:
        stdin_p = None

    gotool = subprocess.Popen(
        cmd,
        stdin=stdin_p,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        env=prepare_env(view, window),
    )
    if stdin is None:
        sout, serr = gotool.communicate()
    else:
        sout, serr = gotool.communicate(stdin.encode())
    if gotool.returncode != 0:
        return gotool.returncode, None, serr.decode()
    return 0, sout.decode(), None


# diff_sanity_check to make sure we change the correct text.
def diff_sanity_check(a, b):
    if a != b:
        raise Exception("diff sanity check mismatch\n-%s\n+%s" % (a, b))


# safe_replace_all attempts to replace existing view with new text.
def safe_replace_all(edit, view, src, dest):
    diff = difflib.ndiff(src.splitlines(), dest.splitlines())
    i = 0
    for line in diff:
        if line.startswith("?"):  # skip hint lines
            continue

        length = (len(line) - 2) + 1
        if line.startswith("-"):
            diff_sanity_check(view.substr(
                sublime.Region(i, i + length - 1)), line[2:])
            view.erase(edit, sublime.Region(i, i + length))
        elif line.startswith("+"):
            view.insert(edit, i, line[2:] + "\n")
            i += length
        else:
            diff_sanity_check(view.substr(
                sublime.Region(i, i + length - 1)), line[2:])
            i += length


# get_byte_offset returns the current byte offset
def get_byte_offset(view):
    cur_char_offset = view.sel()[0].begin()
    text = view.substr(sublime.Region(0, cur_char_offset))
    byte_offset = len(text.encode())
    if view.line_endings() == "Windows":
        byte_offset += text.count('\n')
    return byte_offset


# get_file_archive generate stdin of modified files in the format that guru can understand.
def get_file_archive(view):
    text = view.substr(sublime.Region(0, view.size()))
    byte_size = len(text.encode())
    result = "\n".join([
        view.file_name(),
        str(byte_size),
        text,
    ])
    return result


def _get_goroot(view=None, window=None):
    return _get_most_specific_setting("goroot", view, window)


def _get_gopath(view=None, window=None):
    gopath = _get_most_specific_setting("gopath", view, window)
    if len(gopath) > 0:
        return gopath

    file_path = view.file_name()
    while len(file_path) > 4:
        if os.path.basename(file_path) == "src":
            return os.path.dirname(file_path)
        file_path = os.path.dirname(file_path)
    return ""


def _get_most_specific_setting(name, view=None, window=None):
    """
    Copied from https://github.com/golang/sublime-config/blob/master/all/golangconfig.py
    """

    if view is not None and not isinstance(view, sublime.View):
        raise TypeError("view must be an instance of sublime.View")

    if window is not None and not isinstance(window, sublime.Window):
        raise TypeError("window must be an instance of sublime.Window")

    st_settings = sublime.load_settings("golang.sublime-settings")

    if view and not window:
        window = view.window()

    if window and not view:
        view = window.active_view()

    view_settings = view.settings().get("golang", {}) if view else {}
    window_settings = window.project_data().get("settings", {}).get("golang", {}) if window else {}

    settings_objects = [
        (view_settings, 'project file'),
        (window_settings, 'project file'),
        (st_settings, 'golang.sublime-settings'),
    ]

    for settings_object, source in settings_objects:
        platform_settings = settings_object.get(_platform, "")
        if isinstance(platform_settings, dict) and platform_settings.get(name, "") != "":
            return platform_settings.get(name)

        result = settings_object.get(name, "")
        if result != "":
            return settings_object.get(name)

    return ""


def _check_executable(p):
    return os.path.exists(p) and os.path.isfile(p) and os.access(p, os.X_OK)
