import difflib
import os
import sublime
import subprocess


# is_go_view return true/false whether the given view is for a go source code or not.
def is_go_view(view):
    return view.match_selector(0, "source.go")


def gopath_from_path(path=""):
    while len(path) > 4:
        if os.path.basename(path) == "src":
            return os.path.dirname(path)
        path = os.path.dirname(path)
    return ""


def prepare_env(current_path="", env=os.environ):
    go_path = gopath_from_path(current_path)
    go_path_bin = os.path.join(go_path, "bin")
    my_env = env.copy()
    my_env["PATH"] = ":".join([my_env["PATH"], go_path_bin])
    my_env["GOPATH"] = go_path
    my_env["GOROOT"] = "/usr/local/go"
    return my_env


# run_go_tool executes a go tool command and return code, stdout, stderr.
def run_go_tool(cmd, stdin=None, file_path=None):
    stdin_p = subprocess.PIPE
    if stdin is None:
        stdin_p = None

    gotool = subprocess.Popen(
        cmd,
        stdin=stdin_p,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        env=prepare_env(file_path, os.environ),
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
