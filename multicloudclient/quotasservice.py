import command
import quotasupdate
import pdb

class QuotaSet(command.OpenStackCommand):
    """Updating quotas in multiple regions
       Including the parser for specific quota update commands
    """
    api = 'multi-cloud'
    resource = "tenants"

    # This method adds parsing arguments to the command parser.
    def get_parser(self, prog_name):
        parser = super(QuotaSet, self).get_parser(prog_name)
        parser.add_argument(
        '-D', '--show-details',
        help=('Show detailed information.'),
        action='store_true',
        default=False)
        parser.add_argument(
        '--overcommit',
        metavar='<oversize ram>',
        default=None,
        help=('Oversizing ram 2:1 Or 3:1'))
        parser.add_argument(
        '--instances',
        metavar='<instances>',
        type=int, default=None,
        help=('New value for the "instances" quota.'))
        parser.add_argument(
        '--cores',
        metavar='<cores>',
        type=int, default=None,
        help=('New value for the "cores" quota.'))
        parser.add_argument(
        '--ram',
        metavar='<ram>',
        type=int, default=None,
        help=('New value for the "ram" quota.'))
        parser.add_argument(
        '--key-pairs',
        metavar='<key-pairs>',
        type=int,
        default=None,
        help=('New value for the "key-pairs" quota.'))
        parser.add_argument(
        '--regions', metavar='regions',required=True,
        help=('The owner regions'))
        parser.add_argument(
        '--tenant',
        metavar='<tenant-name>',required=True,
        help=('ID of tenant to set the quotas for.'))
        parser.add_argument(
        '--user',
        metavar='<user-id>',
        default=None,
        help=('ID of user to set the quotas for.'))
        parser.add_argument('--o',action='store_true', default=False, help=('Flag for overwriting quota'))
        parser.add_argument('--3X',action='store_true', default=False ,help=('Flag if 3x VM is needed'))
        return parser
   
    # Call quota update script in quotasupdate.py
    def get_data(self, parsed_args):
        quotasupdate.mainmethod(parsed_args)

