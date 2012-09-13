import simplejson
import sys
from subprocess import call, check_call, CalledProcessError
import shlex

def run_basic_command(cmd_str, check = True):
    f = check_call if check else call
    return f(shlex.split(cmd_str))

def tmux_cmd(args, check = True):
    return run_basic_command("tmux " + args, check = check)

def parse_config(config_file_location):
    """
    Takes a configuration file in the specified json
    format and parses it.
    """
    try:
        with open(config_file_location) as f:
            contents = f.read()
            return simplejson.loads(contents)
    except IOError:
        print "No such template/project name.. exiting."
        sys.exit(1)


class ConfigProcessor(object):

    def __init__(self, config_file_location):
        self.config = parse_config(config_file_location)

        try:
            self.session_name = self.config["session_name"]
        except KeyError:
            print "Config must specify session_name"
            sys.exit(1)

        self.windows = list(enumerate(self.config.get("windows", [])))

    def tmux_cmd_with_config(self, args, check = True):
        return tmux_cmd(args % self.config, check = check)

    def execute_preamble(self):

        # If session already exists.. attach to it and quit
        if tmux_cmd("has-session -t %s" % self.session_name, check = False) == 0:
            print "Session %s already exists.. attaching" % self.session_name
            tmux_cmd("-2 attach -t %s" % (self.session_name,))
            sys.exit(0)

        tmux_cmd("start-server")
        tmux_cmd("new-session -d -s %s -n shell" % (self.session_name,))
        return True

    def process_window(self, index, window_dict):
        window_dict['session'] = self.session_name
        window_dict['index'] = index

        def tmux_cmd_targeting_window(cmd, arg_str = None, pane = None):
            cmd_str = cmd
            print "cmd_str: ", cmd_str
            cmd_str += " -t %(session)s:%(index)d" % window_dict
            print "cmd_str: ", cmd_str
            cmd_str += ".%d " % (pane, ) if pane is not None else " "
            print "cmd_str: ", cmd_str

            if arg_str is not None:
                print "arg_str: ", arg_str
                cmd_str += arg_str % window_dict
                print "cmd_str: ", cmd_str

            return tmux_cmd(cmd_str)

        tmux_cmd_targeting_window("new-window", "-n %(name)s")

        panes = window_dict.get("panes")
        if panes is not None:
            for i, x in enumerate(panes):
                if i == 0: continue
                tmux_cmd_targeting_window("split-window")

            for n, pane_conf in enumerate(panes):
                for cmd in pane_conf.get("commands", []):
                    tmux_cmd_targeting_window("send-keys", "\"%s\" C-m" % (cmd,), pane = n)

        window_layout = window_dict.get('layout')
        if window_layout is not None:
            tmux_cmd_targeting_window("select-layout", "%(layout)s")

        return True

    def execute_window_processing(self):
        for i, window_dict in self.windows:
            self.process_window(i+1, window_dict)

        return True

    def execute_prologue(self):
        self.tmux_cmd_with_config("select-window -t %(session_name)s:0")
        self.tmux_cmd_with_config("-2 attach-session -d -t %(session_name)s")

    def run(self):

        try:
            self.execute_preamble()
            self.execute_window_processing()
            self.execute_prologue()

            return True
        except CalledProcessError:
            print "Error occured starting tmux.. probably a bad config option.  Cleaning up.."
            tmux_cmd("kill-server -t %s" % (self.session_name, ), check = False)
            return False

