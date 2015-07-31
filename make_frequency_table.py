#!/usr/bin/env python

import sys
import csv
from operator import attrgetter
import click
from orthomcl_to_fasta import ProjectInfo, process_orthomcl


def group_frequencies(group_id, members, project, species_position, writer):
    totals = [0] * len(species_position)
    for member in members:
        totals[species_position[member.species.tag]] += 1
    row = [group_id]
    row.extend(totals)
    if totals[0] > 0:
        writer.writerow(row)


@click.command()
@click.option('--fastortho/--no-fastortho', default=True)
@click.argument('project_file', type=click.File())
@click.argument('orthomcl_file', type=click.File())
@click.argument('output_file', type=click.File('w'), default=sys.stdout)
def make_frequency_table(orthomcl_file, project_file, output_file, fastortho=True):
    project = ProjectInfo()
    project.config_from_file(project_file)
    species_list = [project.species_by_tag('sbt')]
    for species in sorted(project.species_list, key=attrgetter('tag')):
        if species.tag != 'sbt':
            species_list.append(species)
    writer = csv.writer(output_file)
    header = ['']  # start with an empty string to keep top-left cell empty
    header.extend(['{} {} ({})'.format(species.genus, species.species, species.tag) for species in species_list])
    writer.writerow(header)
    species_position = dict()
    position = 0
    for species in species_list:
        species_position[species.tag] = position
        position += 1

    process_orthomcl(orthomcl_file, project, fastortho, group_frequencies, species_position, writer)

if __name__ == '__main__':
    make_frequency_table()
