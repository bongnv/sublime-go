import os
from SublimeLinter.lint import util, Linter

from . import utils


class Gotype(Linter):
    regex = r'^.+:(?P<line>\d+):(?P<col>\d+):\s+(?P<message>.+)'
    error_stream = util.STREAM_STDERR
    defaults = {
        'selector': 'source.go'
    }

    def cmd(self):
        filename = self.view.file_name()
        return [
            utils.executable_path("gotype-live", self.view),
            "-e",
            "-seq",
            "-lf="+filename,
            os.path.dirname(filename),
        ]

    def get_environment(self, settings):
        return utils.prepare_env(self.view)


class Golint(Linter):
    regex = r'^.+:(?P<line>\d+):(?P<col>\d+):\s+(?P<message>.+)'
    tempfile_suffix = '-'
    error_stream = util.STREAM_STDOUT
    defaults = {
        'selector': 'source.go'
    }

    def cmd(self):
        return [utils.executable_path("golint", self.view), "$file"]

    def get_environment(self, settings):
        return utils.prepare_env(self.view)


class Govet(Linter):
    regex = r'.+?:(?P<line>\d+):((?P<col>\d+):)?\s+(?P<message>.+)'
    tempfile_suffix = '-'
    error_stream = util.STREAM_STDERR
    defaults = {
        'selector': 'source.go'
    }

    def cmd(self):
        return [utils.executable_path("go", self.view), "tool", "vet", "$file"]

    def get_environment(self, settings):
        return utils.prepare_env(self.view)


class Megacheck(Linter):
    regex = r'^.+:(?P<line>\d+):(?P<col>\d+):\s+(?P<message>.+)'
    tempfile_suffix = '-'
    error_stream = util.STREAM_STDOUT
    defaults = {
        'selector': 'source.go'
    }

    def cmd(self):
        return [utils.executable_path("megacheck", self.view), "$file"]

    def get_environment(self, settings):
        return utils.prepare_env(self.view)

    def should_lint(self, reason):
        return super().should_lint(reason) and reason == 'on_user_request'
