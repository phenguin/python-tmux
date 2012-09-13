from helpers import generate_complete_tmux_script
import argparse
import os
from glob import glob

config_dir = "/home/jcullen/.pythontmux"
template_ext = ".json"
script_ext = ".pymux"

def templates_glob(config_dir_location):
    return os.path.join(get_templates_dir(config_dir_location), "*" + template_ext)

def scripts_glob(config_dir_location):
    return os.path.join(get_scripts_dir(config_dir_location), "*" + script_ext)

def get_scripts_dir(config_dir_location):
    return os.path.join(config_dir, 'scripts')

def get_templates_dir(config_dir_location):
    return os.path.join(config_dir, 'templates')

def get_template_names(config_dir_location):
    templates_dir = get_templates_dir(config_dir_location)
    map_func = lambda x : os.path.splitext(os.path.basename(x))[0]
    return map(map_func, glob(templates_glob(config_dir_location)))

def get_script_names(config_dir_location):
    scripts_dir = get_scripts_dir(config_dir_location)
    map_func = lambda x : os.path.splitext(os.path.basename(x))[0]
    return map(map_func, glob(scripts_glob(config_dir_location)))

def get_template_full_path(config_dir_location, template_name):
    templates_dir = get_templates_dir(config_dir_location)
    return os.path.join(templates_dir, template_name + template_ext)

def get_script_full_path(config_dir_location, template_name):
    scripts_dir = get_scripts_dir(config_dir_location)
    return os.path.join(scripts_dir, template_name + script_ext)

def update(config_dir):
    scripts_dir = get_scripts_dir(config_dir)
    templates_dir = get_templates_dir(config_dir)
    template_names = get_template_names(config_dir)

    for template_name in template_names:
        template_full_path = get_template_full_path(config_dir, template_name)
        write_path = get_script_full_path(config_dir, template_name)
        with open(write_path, 'w') as f:
                f.write(generate_complete_tmux_script(template_full_path))

    return get_script_names(config_dir)

def run(options):
    templates_dir = get_templates_dir(options.configdir)
    scripts_dir = get_scripts_dir(options.configdir)

    existing_scripts = update(options.configdir)

    if options.command == 'edit':
        os.system("$EDITOR %s" % (os.path.join(templates_dir, options.template + ".json"),))
    elif options.command == 'run':
        os.system("sh %s" % (os.path.join(scripts_dir,
            options.template + ".pymux"),))
    elif options.command == 'show':
        for name in existing_scripts:
            print name
    else:
        print "Unknown command: %s" % options.command

def main():
    parser = argparse.ArgumentParser(description='Run tmux sessions defined by json configuration files')
    parser.add_argument("command", choices = ["run", "edit", "show"])
    parser.add_argument("template",
            default="",
            type=str,
            help="Name of template")
    parser.add_argument("--configdir",
            type=str,
            default=config_dir,
            help='Override configuration directory location')
    options = parser.parse_args()
    run(options)

if __name__ == '__main__':
    try:
        main()
    except Exception:
        raise
        print "\n\nSomething unexpected happened!"
        exit(1)
