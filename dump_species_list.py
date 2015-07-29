#!/usr/bin/env python


import sys
from collections import OrderedDict
sys.path.append('/home/pvh/PycharmProjects/seabass/src/seabass_db')
from seabass_model import *
import click
import yaml


@click.command()
@click.option('--connect_string', default='postgres:///seabass_db')
@click.argument('output_file', required=False, default=sys.stdout, type=click.File(mode='w'))
def dump_species_list(connect_string, output_file):
    session = get_session(connect_string)
    species_list = session.query(Species).order_by(Species.abbreviation)
    species_config = dict(species_list=[])
    for species in species_list:
        species_dict = dict(common_name=str(species.common_name),
                            tag=str(species.abbreviation),
                            genus=str(species.genus),
                            species=str(species.species))
        species_config['species_list'].append(species_dict)
    yaml.dump(species_config, output_file, default_flow_style=False)

if __name__ == '__main__':
    dump_species_list()
