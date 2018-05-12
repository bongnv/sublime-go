import os
from SublimeLinter.lint import util, Linter

from . import utils


class Golint(Linter):
    regex = r'^.+:(?P<line>\d+):(?P<col>\d+):\s+(?P<message>.+)'
    tempfile_suffix = '-'
    error_stream = util.STREAM_STDERR
    defaults = {
        'selector': 'source.go'
    }

    def cmd(self):
        file_path = self.view.file_name()
        gopath = utils.gopath_from_path(file_path)
        return os.path.join(gopath, "bin", "golint")
