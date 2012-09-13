from helpers import ConfigProcessor
import argparse
import os
from shutil import copyfile
from glob import glob

config_dir = "/home/jcullen/.pythontmux"
template_ext = ".json"
default_template_name = "default"

def templates_glob(config_dir_location):
    return os.path.join(get_templates_dir(config_dir_location), "*" + template_ext)

def get_templates_dir(config_dir_location):
    return os.path.join(config_dir, 'templates')

def get_template_names(config_dir_location):
    templates_dir = get_templates_dir(config_dir_location)
    map_func = lambda x : os.path.splitext(os.path.basename(x))[0]
    return map(map_func, glob(templates_glob(config_dir_location)))

def get_template_full_path(config_dir_location, template_name):
    templates_dir = get_templates_dir(config_dir_location)
    return os.path.join(templates_dir, template_name + template_ext)

def run_template(config_dir, template_name):
    path = get_template_full_path(config_dir, template_name)
    return ConfigProcessor(path).run()

def remove_template(config_dir, template_name):
    print "Removing template: %s.." % (template_name, )

    try:
        os.remove(get_template_full_path(config_dir, template_name))
    except OSError:
        print "Template %s doesnt exist, doing nothing" % (template_name,)

def template_exists(config_dir, template_name):
    try:
        with open(get_template_full_path(config_dir, template_name)):
            return True
    except IOError:
        return False

# XXX: Nicer errors
def edit_template(config_dir, template_name):

    if not template_exists(config_dir, template_name):
        default_template_path = get_template_full_path(config_dir, default_template_name)
        copyfile(default_template_path, get_template_full_path(config_dir, template_name))

    return os.system("$EDITOR %s" % (get_template_full_path(config_dir, template_name),))

def run(options):
    templates_dir = get_templates_dir(options.configdir)

    if options.command == 'edit':
        edit_template(options.configdir, options.template)
    elif options.command == 'remove':
        remove_template(options.configdir, options.template)
    elif options.command == 'run':
        run_template(options.configdir, options.template)
    elif options.command == 'show':
        for name in get_template_names(options.configdir):
            if name != default_template_name:
                print name
    else:
        print "Unknown command: %s" % options.command

def main():
    parser = argparse.ArgumentParser(description='Run tmux sessions defined by json configuration files')
    parser.add_argument("command", choices = ["run", "edit", "show", "remove"])
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
