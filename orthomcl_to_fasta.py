#!/usr/bin/env python
import sys
import os.path
import click
import yaml
from Bio import SeqIO
from Bio.Alphabet import generic_protein


class ProjectInfo(object):

    def __init__(self, name=None):
        self.project_name = None
        self.species_list = []

    def species_by_tag(self, tag):
        species_list = [species for species in self.species_list if species.tag == tag]
        if len(species_list) == 0:
            return(None)
        else:
            return(species_list[0])

    def add_species(self, species):
        if self.species_by_tag(species.tag) == None:
            self.species_list.append(species)

    def config_from_file(self, config_file):
        project_config = yaml.load(config_file)
        self.name = project_config['name']
        for species in project_config['species_list']:
            species_obj = Species(species['tag'],
                                  species['common_name'],
                                  species['genus'],
                                  species['species'])
            self.add_species(species_obj)


class Species(object):

    def __init__(self, tag, common_name, genus, species):
        self.tag = tag
        self.common_name = common_name
        self.genus = genus
        self.species = species
        self.filename = None
        self._open = False

    def is_open(self):
        return self._open

    def get_filename(self, input_directory):
        filename = os.path.join(input_directory, self.tag + '.fasta')
        return filename

    def find_and_open(self, input_directory):
        filename = self.get_filename(input_directory)
        if not os.path.isfile(filename):
            return False
        else:
            self.filename = filename
            self.index_filename = filename.replace('.fasta', '.idx')
            self.index = SeqIO.index_db(self.index_filename, self.filename, 'fasta', generic_protein)
            self._open = True
            return True

    def __len__(self):
        return len(self.index) if self._open else 0

    def __getitem__(self, id):
        return self.index[id] if self._open else None

    def __str__(self):
        return(self.tag)


class Sequence(object):

    def __init__(self, id, tag, project=None):
        self.id = id
        self.tag = tag
        if project is not None:
            self.species = project.species_by_tag(tag)
        else:
            self.species = None

    def __str__(self):
        return(self.id)


def parse_fastortho(line, project, one_based=False):
    def member_from_string(member):
        fields = member.split('(')
        member_id = fields[0]
        member_tag = fields[1][:-1]
        return Sequence(member_id, member_tag, project=project)

    project_name = project.name if project is not None else 'ORTHOMCL'
    fields = line.rstrip().split()
    group_id = fields[0]
    if project_name != 'ORTHOMCL':
        group_id = group_id.replace('ORTHOMCL', project_name, 1)
    if one_based:
        num_start = len(project_name)
        group_num = int(group_id[num_start:])
        new_group_num = group_num + 1
        group_id = project_name + str(new_group_num)
    members = [member_from_string(member) for member in fields[4:]]
    return(group_id, members)


def parse_orthomcl(line, project):
    def member_from_string(member):
        fields = member.split('|')
        member_id = member
        member_tag = fields[0]
        return Sequence(member_id, member_tag, project=project)

    fields = line.rstrip().split()
    group_id = fields[0][:-1]
    members = [member_from_string(member) for member in fields[1:]]
    return(group_id, members)


def group_to_fasta(group_id, members, project, input_directory, output_directory):
    output_filename = os.path.join(output_directory, group_id + '.fasta')
    sequence_collection = []
    for member in members:
        species = project.species_by_tag(member.tag)
        if not species.is_open():
            ok = member.species.find_and_open(input_directory)
            if not ok:
                sys.exit("Failed to open sequence file {}".format(species.get_filename(input_directory)))
        try:
            sequence_record = species[member.id]
        except KeyError:
            sys.exit("Failed to find {} for {}".format(member.id, species))
        sequence_collection.append(sequence_record)
    SeqIO.write(sequence_collection, output_filename, 'fasta')


def process_orthomcl(orthomcl_file, project, fastortho, worker_func, *args):
    with orthomcl_file:
        for line in orthomcl_file:
            if fastortho and not line.startswith('ORTHOMCL'):
                sys.exit("Format error: FastOrtho groups are expected to start with ORTHOMCL")
            if fastortho:
                (group_id, members) = parse_fastortho(line, project, one_based=True)
            else:
                (group_id, members) = parse_orthomcl(line, project)
            worker_func(group_id, members, project, *args)


@click.command()
@click.option('--fastortho/--no-fastortho', default=True)
@click.argument('project_file', type=click.File())
@click.argument('orthomcl_file', type=click.File())
@click.argument('input_directory', type=click.Path(exists=True, dir_okay=True, file_okay=False))
@click.argument('output_directory', type=click.Path(file_okay=False, dir_okay=True))
def orthomcl_to_fasta(project_file, orthomcl_file, input_directory, output_directory, fastortho=True):
    project = ProjectInfo()
    project.config_from_file(project_file)
    if not os.path.exists(output_directory):
        os.mkdir(output_directory)
    process_orthomcl(orthomcl_file, project, fastortho, group_to_fasta, input_directory, output_directory)

if __name__ == '__main__':
    orthomcl_to_fasta()
