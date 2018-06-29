import difflib
import os
import sys
import subprocess


_platform = {
    'win32': 'windows',
    'darwin': 'osx'
}.get(sys.platform, 'linux')


# get_setting returns setting value of a given name
def get_merged_setting(api, name, view=None, window=None):
    value = {}
    for setting in reversed(_get_all_settings(api, view, window)):
        value.update(setting.get(name, {}))
    return value


# is_go_view return true/false whether the given view is for a go source code or not.
def is_go_view(view=None):
    return view and view.match_selector(0, "source.go")


def executable_path(api, cmd, view=None, window=None):
    for dir_ in prepare_env(api, view, window).get("PATH", "").split(os.pathsep):
        p = os.path.join(dir_, cmd)
        if _check_executable(p):
            return p
    return cmd


def prepare_env(api, view=None, window=None):
    gopath = _get_gopath(api, view, window)
    goroot = _get_goroot(api, view, window)

    my_env = os.environ.copy()
    print(my_env)
    paths = [my_env["PATH"]]
    if len(gopath) > 0:
        paths.append(os.path.join(gopath, "bin"))
        if "GOPATH" not in my_env:
            my_env["GOPATH"] = gopath

    if len(goroot) > 0:
        print(goroot)
        paths.append(os.path.join(goroot, "bin"))
        if "GOROOT" not in my_env:
            my_env["GOROOT"] = goroot

    my_env["PATH"] = os.pathsep.join(paths)
    return my_env


# run_go_tool executes a go tool command and return code, stdout, stderr.
def run_go_tool(api, cmd, stdin=None, view=None, window=None):
    stdin_p = subprocess.PIPE
    if stdin is None:
        stdin_p = None

    gotool = subprocess.Popen(
        cmd,
        stdin=stdin_p,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        env=prepare_env(api, view, window),
    )
    if stdin is None:
        sout, serr = gotool.communicate()
    else:
        sout, serr = gotool.communicate(stdin.encode())
    if gotool.returncode != 0:
        return gotool.returncode, None, serr.decode()
    return 0, sout.decode(), None


# safe_replace_all attempts to replace existing view with new text.
def safe_replace_all(api, view, edit, src, dest):
    diff = difflib.ndiff(src.splitlines(), dest.splitlines())
    i = 0
    for line in diff:
        if line.startswith("?"):  # skip hint lines
            continue

        length = (len(line) - 2) + 1
        if line.startswith("-"):
            _diff_sanity_check(view.substr(
                api.new_region(i, i + length - 1)), line[2:])
            view.erase(edit, api.new_region(i, i + length))
        elif line.startswith("+"):
            view.insert(edit, i, line[2:] + "\n")
            i += length
        else:
            _diff_sanity_check(view.substr(
                api.new_region(i, i + length - 1)), line[2:])
            i += length


# get_byte_offset returns the current byte offset
def get_byte_offset(api, view):
    cur_char_offset = view.sel()[0].begin()
    text = view.substr(api.new_region(0, cur_char_offset))
    byte_offset = len(text.encode())
    if view.line_endings() == "Windows":
        byte_offset += text.count('\n')
    return byte_offset


# get_file_archive generate stdin of modified files in the format that guru can understand.
def get_file_archive(api, view):
    text = view.substr(api.new_region(0, view.size()))
    byte_size = len(text.encode())
    result = "\n".join([
        view.file_name(),
        str(byte_size),
        text,
    ])
    return result


def get_working_dir(api, view=None, window=None):
    view, window = _get_view_window(api, view, window)
    if view and view.file_name():
        return os.path.dirname(view.file_name())
    if window:
        return window.extract_variables()["file_path"]
    return None


def print_output(api, p, view, window=None):
    view, window = _get_view_window(api, view, window)
    sout = p.communicate(get_file_archive(api, view).encode())[0]
    scratch_file = window.new_file()
    scratch_file.set_scratch(True)
    scratch_file.set_name("Find References")
    scratch_file.run_command("append", {"characters": sout.decode()})
    scratch_file.set_read_only(True)
    settings = scratch_file.settings()
    settings.set(
        'result_file_regex',
        r'(.+\.go):([0-9]+)\.([0-9]+)',
    )


# _diff_sanity_check to make sure we change the correct text.
def _diff_sanity_check(a, b):
    if a != b:
        raise Exception("diff sanity check mismatch\n-%s\n+%s" % (a, b))


# get_most_specific_setting attempts to find a value of a given key from several settings
# and return the most specific one
def _get_most_specific_setting(api, view, window, name):
    """
    Copied from https://github.com/golang/sublime-config/blob/master/all/golangconfig.py
    """

    for settings_object in _get_all_settings(api, view, window):
        platform_settings = settings_object.get(_platform, "")
        if isinstance(platform_settings, dict) and platform_settings.get(name, "") != "":
            return platform_settings.get(name)

        result = settings_object.get(name, "")
        if result != "":
            return settings_object.get(name)

    return ""


def _get_goroot(api, view, window):
    goroot = _get_most_specific_setting(api, view, window, "goroot")
    if len(goroot) > 0:
        return goroot

    for path in os.environ.get("PATH").split(os.pathsep):
        if os.path.basename(path) == "bin" and \
                _check_executable(os.path.join(path, "go")):
            return os.path.dirname(path)
    return None


def _get_gopath(api, view, window):
    view, window = _get_view_window(api, view, window)
    gopath = _get_most_specific_setting(api, view, window, "gopath")
    if len(gopath) > 0:
        return gopath

    file_path = view.file_name()
    while len(file_path) > 4:
        if os.path.basename(file_path) == "src":
            return os.path.dirname(file_path)
        file_path = os.path.dirname(file_path)
    return ""


def _get_all_settings(api, view=None, window=None):
    view, window = _get_view_window(api, view, window)
    project_data = window.project_data() or {}

    return [
        project_data.get("golang", {}) if window else {},
        project_data.get("settings", {}).get("golang", {}) if window else {},
        view.settings().get("golang", {}) if view else {},
    ]


def _get_view_window(api, view=None, window=None):
    if view and window is None:
        return view, view.window()
    if window is None:
        window = api.active_window()
    if view is None and window:
        return window.active_view(), window
    return view, window


def _check_executable(p):
    return os.path.exists(p) and os.path.isfile(p) and os.access(p, os.X_OK)
