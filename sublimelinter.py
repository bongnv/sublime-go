import os
from SublimeLinter.lint import util, Linter

from . import utils


class Golint(Linter):
    regex = r'^.+:(?P<line>\d+):(?P<col>\d+):\s+(?P<message>.+)'
    tempfile_suffix = '-'
    defaults = {
        'selector': 'source.go'
    }

    def cmd(self):
        file_path = self.view.file_name()
        gopath = utils.gopath_from_path(file_path)
        return os.path.join(gopath, "bin", "golint")

    def parse_output(self, proc, virtual_view):
        out = proc.stderr
        if len(out) == 0:
            out = proc.stdout
        return self.parse_output_via_regex(out, virtual_view)


class Govet(Linter):
    regex = r'^(?!vet:).+:(?P<line>\d+)(:(?P<col>\d+))?:\s+(?P<message>.+)'
    tempfile_suffix = '-'
    error_stream = util.STREAM_STDERR
    defaults = {
        'selector': 'source.go'
    }

    def __init__(self, view, syntax):
        super().__init__(view, syntax)
        file_path = self.view.file_name()
        self.gopath = utils.gopath_from_path(file_path)
        self.env = {"GOPATH": self.gopath}

    def cmd(self):
        return os.path.join(self.gopath, "bin", "govet")
