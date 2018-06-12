import json
import os
import sublime
import sublime_plugin
import subprocess
import threading

from . import utils


# A list of the environment variables to pull from settings when creating a
# subprocess. Some subprocesses may have one or more manually overridden.
GO_ENV_VARS = set([
    'GOPATH',
    'GOROOT',
    'GOROOT_FINAL',
    'GOBIN',
    'GOHOSTOS',
    'GOHOSTARCH',
    'GOOS',
    'GOARCH',
    'GOARM',
    'GO386',
    'GORACE',
])


class GoFormatCommand(sublime_plugin.TextCommand):
    def is_enabled(self):
        return utils.is_go_view(self.view)

    def run(self, edit, cmd):
        view = self.view
        if not utils.is_go_view(view):
            return
        src = view.substr(sublime.Region(0, view.size()))
        filename = view.file_name()

        cmd = [x.format_map({"file": filename}) for x in cmd]
        code, sout, serr = utils.run_go_tool(
            cmd,
            src,
            view,
        )
        if code != 0:
            print("error while running goimports, err: " + serr)
            return

        utils.safe_replace_all(edit, view, src, sout)


class GoGuruGotoCommand(sublime_plugin.TextCommand):
    def is_enabled(self):
        return utils.is_go_view(self.view)

    def run(self, edit):
        if not utils.is_go_view(self.view):
            return

        filename = self.view.file_name()
        offset = utils.get_byte_offset(self.view)

        code, sout, serr = utils.run_go_tool(
            ["guru", "-json", "-modified", "definition", filename + ":#" + str(offset)],
            stdin=utils.get_file_archive(self.view),
            view=self.view,
        )

        if code != 0:
            print(serr)
            return

        definition = json.loads(sout)
        position = definition['objpos']
        self.view.window().open_file(position, sublime.ENCODED_POSITION)


# Codes are modified from a copy https://www.sublimetext.com/docs/3/build_systems.html
class GoBuildCommand(sublime_plugin.WindowCommand):
    encoding = 'utf-8'
    killed = False
    proc = None
    panel = None
    panel_lock = threading.Lock()

    def is_enabled(self, lint=False, integration=False, kill=False):
        if not utils.is_go_view(self.view):
            return False

        # The Cancel build option should only be available
        # when the process is still running
        if kill:
            return self.proc is not None and self.proc.poll() is None
        return True

    def run(self, task="build", flags=None, kill=False):
        if kill:
            if self.proc:
                self.killed = True
                self.proc.terminate()
            return

        working_dir = utils.get_working_dir(window=self.window)

        # A lock is used to ensure only one thread is
        # touching the output panel at a time
        with self.panel_lock:
            # Creating the panel implicitly clears any previous contents
            self.panel = self.window.create_output_panel('go_build')

            # Enable result navigation. The result_file_regex does
            # the primary matching, but result_line_regex is used
            # when build output includes some entries that only
            # contain line/column info beneath a previous line
            # listing the file info. The result_base_dir sets the
            # path to resolve relative file names against.
            settings = self.panel.settings()
            settings.set(
                'result_file_regex',
                r'^File "([^"]+)" line (\d+) col (\d+)'
            )
            settings.set(
                'result_line_regex',
                r'^\s+line (\d+) col (\d+)'
            )
            settings.set('result_base_dir', working_dir)
            settings.set('scroll_past_end', False)

            self.window.run_command('show_panel', {'panel': 'output.go_build'})

        if self.proc is not None:
            self.proc.terminate()
            self.proc = None

        args = ["go", task]
        if flags and isinstance(flags, list):
            args.extend(flags)

        env = utils.prepare_env(window=self.window)

        self.proc = subprocess.Popen(
            args,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            cwd=working_dir,
            env=env,
        )
        self.killed = False
        self.write_header(args, working_dir, env)
        threading.Thread(
            target=self.read_handle,
            args=(self.proc.stdout,)
        ).start()

    def write_header(self, args, cwd, env):
        title = ''

        env_vars = []
        for var_key in GO_ENV_VARS:
            if var_key in env:
                value = env.get(var_key)
                env_vars.append((var_key, value))
        if env_vars:
            title += '> Environment:\n'
            for var_name, value in env_vars:
                title += '>   %s=%s\n' % (var_name, value)

        title += '> Directory: %s\n' % cwd
        title += '> Command: %s\n' % subprocess.list2cmdline(args)
        title += '> Output:\n'
        self.queue_write(title)

    def read_handle(self, handle):
        chunk_size = 2 ** 13
        out = b''
        while True:
            try:
                data = os.read(handle.fileno(), chunk_size)
                # If exactly the requested number of bytes was
                # read, there may be more data, and the current
                # data may contain part of a multibyte char
                out += data
                if len(data) == chunk_size:
                    continue
                if data == b'' and out == b'':
                    raise IOError('EOF')
                # We pass out to a function to ensure the
                # timeout gets the value of out right now,
                # rather than a future (mutated) version
                self.queue_write(out.decode(self.encoding))
                if data == b'':
                    raise IOError('EOF')
                out = b''
            except (UnicodeDecodeError) as e:
                msg = 'Error decoding output using %s - %s'
                self.queue_write(msg % (self.encoding, str(e)))
                break
            except (IOError):
                if self.killed:
                    msg = 'Cancelled'
                else:
                    msg = 'Finished'
                self.queue_write('\n[%s]' % msg)
                break

    def queue_write(self, text):
        sublime.set_timeout(lambda: self.do_write(text), 1)

    def do_write(self, text):
        with self.panel_lock:
            self.panel.run_command('insert', {'characters': text})
