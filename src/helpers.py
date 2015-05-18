# coding=utf-8
'''
Helpers for data mining tasks.
'''

import csv, json
from rdflib import Graph, RDF, RDFS, Namespace

DATA_DIR = '../data/'

common_species = {  # Support 0.5 items
    'alli', 'haahka', 'haapana', 'haarapääsky', 'harmaalokki', 'hippiäinen', 'isokoskelo', 'kalalokki', 'korppi',
    'kottarainen', 'kyhmyjoutsen', 'merilokki', 'merimetso', 'mustarastas', 'naurulokki', 'niittykirvinen', 'peippo',
    'punarinta', 'räkättirastas', 'sinisorsa', 'sinitiainen', 'talitiainen', 'telkkä', 'tukkakoskelo', 'tukkasotka',
    'tylli', 'varis', 'varpushaukka', 'viherpeippo', 'vihervarpunen', 'västäräkki'}
#    {
#    # Support 0.75 items:
#    'haahka', 'harmaalokki', 'isokoskelo', 'kalalokki', 'korppi', 'kyhmyjoutsen', 'merilokki', 'naurulokki', 'peippo',
#    'sinisorsa', 'sinitiainen', 'talitiainen', 'telkkä', 'varis', 'viherpeippo', 'vihervarpunen'
#    }

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


def get_all_names(finnish_list):
    '''
    Get scientific name and english name from finnish name

    :param finnish_list:
    :return: list of tuples (finnish, scientific, english)

    >>> get_all_names(['peippo', 'mustavaris'])
    [('peippo', 'Fringilla coelebs', 'chaffinch'),
     ('mustavaris', 'Corvus frugilegus', 'rook')]
    '''
    nsTaxMeOn = Namespace("http://www.yso.fi/onto/taxmeon/")

    taxon_ontology = Graph()
    taxon_ontology.parse(DATA_DIR + 'halias_taxon_ontology.ttl', format='turtle')

    name_list = []

    for finnish in finnish_list:
        taxa = taxon_ontology.subjects(RDF.type, nsTaxMeOn["TaxonInChecklist"])
        for taxon in taxa:
            labels = taxon_ontology.objects(taxon, RDFS.label)
        #    if nsRanks["Species"] in taxon_ontology.objects(taxon, RDF.type):
            save_this = False
            eng = None
            sci = None
            for label in labels:
                if label.language == 'fi' and str(label) == finnish:
                    save_this = True
                elif label.language == 'en':
                    eng = str(label)
                else:
                    # Assume sci
                    sci = str(label)

            if save_this:
                name_list.append((finnish, sci, eng))

    assert len(name_list) == len(finnish_list)

    return name_list