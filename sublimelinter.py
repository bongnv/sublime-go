from SublimeLinter.lint import util, Linter

from . import utils


class Golint(Linter):
    regex = r'^.+:(?P<line>\d+):(?P<col>\d+):\s+(?P<message>.+)'
    tempfile_suffix = '-'
    defaults = {
        'selector': 'source.go'
    }

    def cmd(self):
        cmd = utils.executable_path("golint", self.view)
        print(cmd)
        return cmd

    def get_environment(self, settings):
        return utils.prepare_env(self.view)

    def parse_output(self, proc, virtual_view):
        out = proc.stderr
        if len(out) == 0:
            out = proc.stdout
        return self.parse_output_via_regex(out, virtual_view)


class Govet(Linter):
    regex = r'.+?:(?P<line>\d+):((?P<col>\d+):)?\s+(?P<message>.+)'
    tempfile_suffix = '-'
    error_stream = util.STREAM_STDERR
    defaults = {
        'selector': 'source.go'
    }

    def cmd(self):
        return [utils.executable_path("go", self.view), "tool", "vet"]

    def get_environment(self, settings):
        return utils.prepare_env(self.view)
