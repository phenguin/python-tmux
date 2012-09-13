from helpers import generate_complete_tmux_script
import argparse
import os
from glob import glob

config_dir = "/home/jcullen/.pythontmux"

def get_scripts_dir(config_dir_location):
    return os.path.join(config_dir, 'scripts')

def get_templates_dir(config_dir_location):
    return os.path.join(config_dir, 'templates')

def update(config_dir):
    scripts_dir = get_scripts_dir(config_dir)
    templates_dir = get_templates_dir(config_dir)
    template_names = map(os.path.basename, glob(os.path.join(templates_dir, "*.json")))

    for filename in template_names:
        script_name = os.path.splitext(filename)[0] + ".pymux"
        template_full_path = os.path.join(templates_dir, filename)
        write_path = os.path.join(scripts_dir, script_name)
        with open(write_path, 'w') as f:
                f.write(generate_complete_tmux_script(template_full_path))

    return True

def run(options):
    templates_dir = get_templates_dir(options.configdir)
    scripts_dir = get_scripts_dir(options.configdir)

    update(options.configdir)

    if options.command == 'edit':
        os.system("$EDITOR %s" % (os.path.join(templates_dir, options.template + ".json"),))
    elif options.command == 'run':
        os.system("sh %s" % (os.path.join(scripts_dir,
            options.template + ".pymux"),))
    elif options.command == 'show':
        raise NotImplementedError
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
