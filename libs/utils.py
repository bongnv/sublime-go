import difflib
import os
import sys
import subprocess
import shellenv


_platform = {
    'win32': 'windows',
    'darwin': 'osx'
}.get(sys.platform, 'linux')


# get_setting returns setting value of a given name
def get_merged_setting(cmd, name):
    value = {}
    for setting in reversed(_get_all_settings(cmd)):
        value.update(setting.get(name, {}))
    return value


# is_go_view return true/false whether the given view is for a go source code or not.
def is_go_view(view=None):
    return view and view.match_selector(0, "source.go")


def executable_path(sublime_cmd, cmd):
    for dir_ in prepare_env(sublime_cmd).get("PATH", "").split(os.pathsep):
        p = os.path.join(dir_, cmd)
        if _check_executable(p):
            return p
    return cmd


def prepare_env(cmd):
    gopath = _get_gopath(cmd)
    goroot = _get_goroot(cmd)

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
def run_go_tool(sublime_cmd, cmd, stdin=None):
    stdin_p = subprocess.PIPE
    if stdin is None:
        stdin_p = None

    gotool = subprocess.Popen(
        cmd,
        stdin=stdin_p,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        env=prepare_env(sublime_cmd),
    )
    if stdin is None:
        sout, serr = gotool.communicate()
    else:
        sout, serr = gotool.communicate(stdin.encode())
    if gotool.returncode != 0:
        return gotool.returncode, None, serr.decode()
    return 0, sout.decode(), None


# safe_replace_all attempts to replace existing view with new text.
def safe_replace_all(cmd, src, dest):
    diff = difflib.ndiff(src.splitlines(), dest.splitlines())
    i = 0
    for line in diff:
        if line.startswith("?"):  # skip hint lines
            continue

        length = (len(line) - 2) + 1
        if line.startswith("-"):
            _diff_sanity_check(cmd.view.substr(
                cmd.new_region(i, i + length - 1)), line[2:])
            cmd.view.erase(cmd.edit, cmd.new_region(i, i + length))
        elif line.startswith("+"):
            cmd.view.insert(cmd.edit, i, line[2:] + "\n")
            i += length
        else:
            _diff_sanity_check(cmd.view.substr(
                cmd.new_region(i, i + length - 1)), line[2:])
            i += length


# get_byte_offset returns the current byte offset
def get_byte_offset(cmd):
    cur_char_offset = cmd.view.sel()[0].begin()
    text = cmd.view.substr(cmd.new_region(0, cur_char_offset))
    byte_offset = len(text.encode())
    if cmd.view.line_endings() == "Windows":
        byte_offset += text.count('\n')
    return byte_offset


# get_file_archive generate stdin of modified files in the format that guru can understand.
def get_file_archive(cmd):
    text = cmd.view.substr(cmd.new_region(0, cmd.view.size()))
    byte_size = len(text.encode())
    result = "\n".join([
        cmd.view.file_name(),
        str(byte_size),
        text,
    ])
    return result


def get_working_dir(cmd):
    if cmd.view and cmd.view.file_name():
        return os.path.dirname(cmd.view.file_name())
    if cmd.window:
        return cmd.window.extract_variables()["file_path"]
    return None


def print_output(cmd, p):
    sout = p.communicate(get_file_archive(cmd).encode())[0]
    scratch_file = cmd.window.new_file()
    scratch_file.set_scratch(True)
    scratch_file.set_name("Find References")
    scratch_file.run_command("append", {"characters": sout.decode()})
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
def _get_most_specific_setting(cmd, name):
    """
    Copied from https://github.com/golang/sublime-config/blob/master/all/golangconfig.py
    """

    for settings_object in _get_all_settings(cmd):
        platform_settings = settings_object.get(_platform, "")
        if isinstance(platform_settings, dict) and platform_settings.get(name, "") != "":
            return platform_settings.get(name)

        result = settings_object.get(name, "")
        if result != "":
            return settings_object.get(name)

    return ""


def _get_goroot(cmd):
    return _get_most_specific_setting(cmd, "goroot")


def _get_gopath(cmd):
    gopath = _get_most_specific_setting(cmd, "gopath")
    if len(gopath) > 0:
        return gopath

    file_path = cmd.view.file_name()
    while len(file_path) > 4:
        if os.path.basename(file_path) == "src":
            return os.path.dirname(file_path)
        file_path = os.path.dirname(file_path)
    return ""


def _get_all_settings(cmd):
    project_data = cmd.window.project_data() or {}

    return [
        project_data.get("golang", {}) if cmd.window else {},
        project_data.get("settings", {}).get("golang", {}) if cmd.window else {},
        cmd.view.settings().get("golang", {}) if cmd.view else {},
    ]


def _check_executable(p):
    return os.path.exists(p) and os.path.isfile(p) and os.access(p, os.X_OK)
