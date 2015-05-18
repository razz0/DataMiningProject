# coding=utf-8
'''
Helpers for data mining tasks.
'''

import csv, json

DATA_DIR = '../data/'

common_species = {
    # Support 0.75 items:
    'haahka', 'harmaalokki', 'isokoskelo', 'kalalokki', 'korppi', 'kyhmyjoutsen', 'merilokki', 'naurulokki', 'peippo',
    'sinisorsa', 'sinitiainen', 'talitiainen', 'telkkä', 'varis', 'viherpeippo', 'vihervarpunen'
}
# len(common_species) == 16


def read_observation_basket(filename):
    """
    Read observation itemsets from file.

    :param filename:
    """
    itemsets = []

    with open(filename) as csvfile:
        transaction_reader = csv.reader(csvfile, delimiter=',', skipinitialspace=True)
        for row in transaction_reader:
            itemsets.append(tuple(sorted(row)))

    return itemsets


def get_species(itemsets):
    return set([species for itemset in itemsets for species in itemset])


def read_observation_sequences(filename):
    """
    Read observation sequences from file.

    :param filename: sequence file (JSON)
    """
    with open(filename) as f:
        sequences = json.load(f)

    return sequences


def get_yearly_sequences(prune_common_species = False):
    '''
    Put each years' observations into separate sequence

    :param prune_common_species: Leave out the most commonly (year round) observed species
    :return:
    '''
    sequences = read_observation_sequences(DATA_DIR + 'observation.sequence')
    year_seqs = []

    pruned_species = common_species if prune_common_species else []

    for year in range(1979, 2009):
        good_keys, good_seqs = zip(*[(date, obs) for date, obs in sorted(sequences.items()) if date.startswith(str(year))])

        year_seqs.append([[species for species, _, _ in sorted(seq) if species not in pruned_species]
                          for seq in good_seqs])

    return year_seqs

