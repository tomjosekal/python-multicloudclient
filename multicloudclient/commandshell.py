
from __future__ import print_function

import argparse
import getpass
import inspect
import itertools
import logging
import os
import sys
import multitenantservice
import quotasservice
import six.moves.urllib.parse as urlparse
from cliff import app
from cliff import commandmanager

VERSION = '2.0'
API_VERSION = '2.0'

COMMAND_V2 = {'create-tenants': multitenantservice.CreateTenants,
    'quota-update':quotasservice.QuotaSet
    }

COMMANDS = {'2.0': COMMAND_V2}

def run_command(cmd, cmd_parser, sub_argv):
    _argv = sub_argv
    index = -1
    values_specs = []
    if '--' in sub_argv:
        index = sub_argv.index('--')
        _argv = sub_argv[:index]
       #values_specs = sub_argv[index:]
    known_args = cmd_parser.parse_args(_argv)
    #cmd.values_specs = (index == -1 and _values_specs or values_specs)
    return cmd.run(known_args)


def check_non_negative_int(value):
    try:
        value = int(value)
    except ValueError:
        raise argparse.ArgumentTypeError(_("invalid int value: %r") % value)
    if value < 0:
        raise argparse.ArgumentTypeError(_("input value %d is negative") %
                                         value)
    return value

class HelpAction(argparse.Action):
    """Provide a custom action so the -h and --help options
    to the main app will print a list of the commands.

    The commands are determined by checking the CommandManager
    instance, passed in as the "default" value for the action.
    """
    def __call__(self, parser, namespace, values, option_string=None):
        outputs = []
        max_len = 0
        app = self.default
        parser.print_help(app.stdout)
        app.stdout.write(('\nCommands for API v%s:\n') % app.api_version)
        command_manager = app.command_manager
        for name, ep in sorted(command_manager):
            factory = ep.load()
            cmd = factory(self, None)
            one_liner = cmd.get_description().split('\n')[0]
            outputs.append((name, one_liner))
            max_len = max(len(name), max_len)
        for (name, one_liner) in outputs:
            app.stdout.write('  %s  %s\n' % (name.ljust(max_len), one_liner))
        sys.exit(0)


class MultiTenantShell(app.App):

    # verbose logging levels
    WARNING_LEVEL = 0
    INFO_LEVEL = 1
    DEBUG_LEVEL = 2
    CONSOLE_MESSAGE_FORMAT = '%(message)s'
    DEBUG_MESSAGE_FORMAT = '%(levelname)s: %(name)s %(message)s'
    log = logging.getLogger(__name__)

    def __init__(self, apiversion):
        super(MultiTenantShell, self).__init__(
            description='Command-line interface to the Multi tenant API ',
            version=VERSION,
            command_manager=commandmanager.CommandManager('multitenant.cli'), )
        self.commands = COMMANDS
        for k, v in self.commands[apiversion].items():
            self.command_manager.add_command(k, v)

        #self._register_extensions(VERSION)

        # Pop the 'complete' to correct the outputs of 'multitenant help'.
        self.command_manager.commands.pop('complete')

        # This is instantiated in initialize_app() only when using
        # password flow auth
        self.auth_client = None
        self.api_version = apiversion

    def build_option_parser(self, description, version):
        """Return an argparse option parser for this application.

        Subclasses may override this method to extend
        the parser with more global options.

        :param description: full description of the application
        :paramtype description: str
        :param version: version number for the application
        :paramtype version: str
        """
        parser = argparse.ArgumentParser(
            description=description,
            add_help=False, )
        parser.add_argument(
            '--version',
            action='version',
            version=2, )
        parser.add_argument(
            '-v', '--verbose', '--debug',
            action='count',
            dest='verbose_level',
            default=self.DEFAULT_VERBOSE_LEVEL,
            help=('Increase verbosity of output and show tracebacks on'
                   ' errors. You can repeat this option.'))
        parser.add_argument(
            '-q', '--quiet',
            action='store_const',
            dest='verbose_level',
            const=0,
            help=('Suppress output except warnings and errors.'))
        parser.add_argument(
            '-h', '--help',
            action=HelpAction,
            nargs=0,
            default=self,  # tricky
            help=("Show this help message and exit."))
        parser.add_argument(
            '-r', '--retries',
            metavar="NUM",
            type=check_non_negative_int,
            default=0,
            help=("How many times the request to the server should "
                   "be retried if it fails."))
        # FIXME(bklei): this method should come from python-keystoneclient
        #self._append_global_identity_args(parser)

        return parser
    
    def _bash_completion(self):
        """Prints all of the commands and options for bash-completion."""
        commands = set()
        options = set()
        for option, _action in self.parser._option_string_actions.items():
            options.add(option)
        for command_name, command in self.command_manager:
            commands.add(command_name)
            cmd_factory = command.load()
            cmd = cmd_factory(self, None)
            cmd_parser = cmd.get_parser('')
            for option, _action in cmd_parser._option_string_actions.items():
                options.add(option)
        print(' '.join(commands | options))

    def _register_extensions(self, version):
        for name, module in itertools.chain(
                client_extension._discover_via_entry_points()):
            self._extend_shell_commands(module, version)

    def _extend_shell_commands(self, module, version):
        classes = inspect.getmembers(module, inspect.isclass)
        for cls_name, cls in classes:
            if (issubclass(cls, client_extension.NeutronClientExtension) and
                    hasattr(cls, 'shell_command')):
                cmd = cls.shell_command
                if hasattr(cls, 'versions'):
                    if version not in cls.versions:
                        continue
                try:
                    self.command_manager.add_command(cmd, cls)
                    self.commands[version][cmd] = cls
                except TypeError:
                    pass

    def run(self, argv):
        """Equivalent to the main program for the application.

        :param argv: input arguments and options
        :paramtype argv: list of str
        """
        try:
            index = 0
            command_pos = -1
            help_pos = -1
            help_command_pos = -1
            for arg in argv:
                if arg == 'bash-completion' and help_command_pos == -1:
                    self._bash_completion()
                    return 0
                if arg in self.commands[self.api_version]:
                    if command_pos == -1:
                        command_pos = index
                elif arg in ('-h', '--help'):
                    if help_pos == -1:
                        help_pos = index
                elif arg == 'help':
                    if help_command_pos == -1:
                        help_command_pos = index
                index = index + 1
            if command_pos > -1 and help_pos > command_pos:
                argv = ['help', argv[command_pos]]
            if help_command_pos > -1 and command_pos == -1:
                argv[help_command_pos] = '--help'
            self.options, remainder = self.parser.parse_known_args(argv)
            #self.configure_logging()
            self.interactive_mode = not remainder
            self.initialize_app(remainder)
        except Exception as err:
            if self.options.verbose_level >= self.DEBUG_LEVEL:
                self.log.exception(err)
                raise
            else:
                self.log.error(err)
            return 1
        if self.interactive_mode:
            _argv = [sys.argv[0]]
            sys.argv = _argv
            return self.interact()
        return self.run_subcommand(remainder)

    def run_subcommand(self, argv):
        subcommand = self.command_manager.find_command(argv)
        cmd_factory, cmd_name, sub_argv = subcommand
        cmd = cmd_factory(self, self.options)
        try:
            self.prepare_to_run_command(cmd)
            full_name = (cmd_name
                         if self.interactive_mode
                         else ' '.join([self.NAME, cmd_name])
                         )
            cmd_parser = cmd.get_parser(full_name)
            return run_command(cmd, cmd_parser, sub_argv)
        except Exception as e:
            if self.options.verbose_level >= self.DEBUG_LEVEL:
                self.log.exception("%s", e)
                raise
            self.log.error("%s", e)
        return 1

    def initialize_app(self, argv):
        """Global app init bits:

        * set up API versions
        """

        super(MultiTenantShell, self).initialize_app(argv)

        self.api_version = {'network': self.api_version}

        # If the user is not asking for help, make sure they
        # have given us auth.
        cmd_name = None
        if argv:
            cmd_info = self.command_manager.find_command(argv)
            cmd_factory, cmd_name, sub_argv = cmd_info

def main(argv=sys.argv[1:]):
    try:
        return MultiTenantShell(API_VERSION).run(
            list(argv))
    except KeyboardInterrupt:
        print("... terminating client", file=sys.stderr)
        return 130
    except Exception as e:
        print(e)
        return 1

if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
