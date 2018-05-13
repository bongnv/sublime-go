import os
from SublimeLinter.lint import util, Linter

from . import utils


class Golint(Linter):
    regex = r'^.+:(?P<line>\d+):(?P<col>\d+):\s+(?P<message>.+)'
    tempfile_suffix = '-'
    error_stream = util.STREAM_BOTH
    defaults = {
        'selector': 'source.go'
    }

    def cmd(self):
        file_path = self.view.file_name()
        gopath = utils.gopath_from_path(file_path)
        return os.path.join(gopath, "bin", "golint")


class Govet(Linter):
    regex = r'^.+:(?P<line>\d+)(:(?P<col>\d+))?:\s+(?P<message>.+)'
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
