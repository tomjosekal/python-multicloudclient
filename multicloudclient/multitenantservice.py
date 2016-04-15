from __future__ import print_function

import argparse

from cliff import lister
from cliff import show
import command
import createtenants
import pdb

class CreateTenants(command.OpenStackCommand):
    """Creating tenants 

    """
    #api = 'network'
    resource = "tenants"

    def get_parser(self, prog_name):
	
        parser = super(CreateTenants, self).get_parser(prog_name)
        parser.add_argument(
        '-D', '--show-details',
        help=('Show detailed information.'),
        action='store_true',
        default=False, )
        parser.add_argument(
            '--tenant_id', metavar='tenant-id',required=True,
            help=('The owner tenant ID.'))
        parser.add_argument(
            '--owner',metavar='user',required=True,
            help=('The owner'))
	parser.add_argument(
            '--email', metavar='emailid',required=True,
            help=('The owner email'))
	parser.add_argument(
            '--regions', metavar='regions',required=True,
            help=('The owner regions'))
        return parser

    def run(self, parsed_args):
	regions=parsed_args.regions.split(',')
	key = parsed_args.regions
	createtenants.mainmethod(parsed_args.tenant_id,parsed_args.owner,parsed_args.email,regions)
