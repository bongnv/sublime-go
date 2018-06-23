import os

from . import utils


class Gotype:
    regex = r'(?P<filename>^.+):(?P<line>\d+):(?P<col>\d+):\s+(?P<message>.+)'
    defaults = {
        'selector': 'source.go'
    }

    def __init__(self):
        self.error_stream = self.STREAM_STDERR

    def cmd(self):
        filename = self.view.file_name()
        return [
            utils.executable_path(self, "gotype-live", self.view),
            "-e",
            "-seq",
            "-lf="+filename,
            os.path.dirname(filename),
        ]

    def get_environment(self, settings):
        return utils.prepare_env(self, self.view)

    def split_match(self, match):
        gd = match.groupdict()
        if gd.get("filename") != self.view.file_name():
            return None
        return super().split_match(match)


class Golint:
    regex = r'^.+:(?P<line>\d+):(?P<col>\d+):\s+(?P<message>.+)'
    tempfile_suffix = '-'
    defaults = {
        'selector': 'source.go'
    }

    def __init__(self):
        self.error_stream = self.STREAM_STDOUT

    def cmd(self):
        return [utils.executable_path(self, "golint", self.view), "$file"]

    def get_environment(self, settings):
        return utils.prepare_env(self, self.view)


class Govet:
    regex = r'.+?:(?P<line>\d+):((?P<col>\d+):)?\s+(?P<message>.+)'
    tempfile_suffix = '-'
    defaults = {
        'selector': 'source.go'
    }

    def __init__(self):
        self.error_stream = self.STREAM_STDERR

    def cmd(self):
        return [utils.executable_path(self, "go", self.view), "tool", "vet", "$file"]

    def get_environment(self, settings):
        return utils.prepare_env(self, self.view)


class Megacheck:
    regex = r'^.+:(?P<line>\d+):(?P<col>\d+):\s+(?P<message>.+)'
    tempfile_suffix = '-'
    defaults = {
        'selector': 'source.go'
    }

    def __init__(self):
        self.error_stream = self.STREAM_STDOUT

    def cmd(self):
        return [utils.executable_path(self, "megacheck", self.view), "$file"]

    def get_environment(self, settings):
        return utils.prepare_env(self, self.view)

    def should_lint(self, reason):
        return super().should_lint(reason) and reason == 'on_user_request'
