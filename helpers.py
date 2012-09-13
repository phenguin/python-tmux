import simplejson

def parse_config(config_file_location):
    """
    Takes a configuration file in the specified json
    format and parses it.
    """
    with open(config_file_location) as f:
        contents = f.read()
        return simplejson.loads(contents)

# XXX: Need shell escapes here
def generate_preamble(config_dict):
    config_dict['start_dir'] = config_dict.get('start_dir', '$PWD')
    with open("/home/jcullen/code/python-tmux/preamble.tmux.template") as f:
        preamble = f.read() % config_dict

    return preamble

# XXX: Need shell escapes here
def generate_prologue(config_dict):

    config_dict['start_window'] = config_dict.get('start_window') or 0

    with open("/home/jcullen/code/python-tmux/prologue.tmux.template") as f:
        prologue = f.read() % config_dict

    return prologue

# XXX: Need shell escapes here
def generate_window_setup_code(window_config_list):
    built_string = "\n"
    for i, window_params in enumerate(window_config_list):
        if i == 0:
            built_string += "tmux new-session -d -s $SESSION -n %(name)s\n" % window_params
        else:
            built_string += "tmux new-window -t $SESSION:%d -n %s\n" % (i, window_params['name'])

    return built_string

# XXX: Need shell escapes here
def generate_main_window_code(config_dict):
    default_dir = config_dict.get('start_dir', '$WORKINGDIR')
    window_config_list = config_dict.get('windows', [])
    built_string = "\n"

    for i, window_params in enumerate(window_config_list):
        built_string += \
                "tmux send-keys -t $SESSION:%d \"cd %s; %s\" C-m\n" \
                % (i, window_params.get('start_dir', default_dir), window_params.get('command', ''))

    return built_string

def generate_complete_tmux_script(config_file_location):

    config_dict = parse_config(config_file_location)
    window_config_list = config_dict.get('windows', [])

    return generate_preamble(config_dict) + \
            generate_window_setup_code(window_config_list) + \
            generate_main_window_code(config_dict) + \
            generate_prologue(config_dict)
