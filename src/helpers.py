# coding=utf-8
'''
Helpers for data mining tasks.
'''
from collections import defaultdict

import csv
import json
import math

from rdflib import Graph, RDF, RDFS, Namespace


nsTaxMeOn = Namespace("http://www.yso.fi/onto/taxmeon/")
nsRanks = Namespace("http://www.yso.fi/onto/taxonomic-ranks/")
nsHaliasSchema = Namespace("http://ldf.fi/schema/halias/")


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


def read_observation_sequences(filename=DATA_DIR + 'observation.sequence'):
    """
    Read observation sequences from file.

    :param filename: sequence file (JSON)
    """
    with open(filename) as f:
        sequences = json.load(f)

    return sequences


def get_all_taxa():
    itemsets = read_observation_basket(DATA_DIR + 'observation.basket')
    return list(set([item for itemset in itemsets for item in itemset]))


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


def local_name(uri):
    return uri.split('/')[-1]


def get_species_itemsets():
    '''
    Get data about single species as transactions

    :return:
    '''
    all_taxa = get_all_taxa()

    species_itemsets = []
    species_names = []

    taxon_ontology = Graph()
    taxon_ontology.parse(DATA_DIR + 'halias_taxon_ontology.ttl', format='turtle')

    species_nodes = taxon_ontology.subjects(RDF.type, nsRanks["Species"])

    for sp in species_nodes:
        this_species = []

        labels = taxon_ontology.objects(sp, RDFS.label)
    #    if nsRanks["Species"] in taxon_ontology.objects(taxon, RDF.type):

        for label in labels:
            if label.language == 'fi':
                finnish = str(label)

        if finnish not in all_taxa:
            continue

        this_species.append(finnish)

        conservation_status = next(taxon_ontology.objects(sp, nsHaliasSchema['hasConservationStatus2010']), False)
        if conservation_status:
            this_species.append(local_name(str(conservation_status)))
        rarity = next(taxon_ontology.objects(sp, nsHaliasSchema['rarity']), False)
        if rarity:
            this_species.append(local_name(str(rarity)))
        charas = taxon_ontology.objects(sp, nsHaliasSchema['hasCharacteristic'])
        if charas:
            this_species += ['tuntom: %s' % local_name(str(chara)) for chara in charas]

            # Take only species with characteristics
        species_itemsets.append(this_species)
        species_names.append(finnish)

    seqs = read_observation_sequences()

    sums_pres = defaultdict(int)
    amounts = defaultdict(int)
    sums_temp = defaultdict(int)
    # n_temp = defaultdict(int)

    for date, obses in seqs.items():
        for obs in obses:
            species, count_mig, count_tot, month_num, \
                weather_pressure, weather_cover, weather_humidity, weather_rainfall, weather_temp_day, weather_wind, \
                weather_std_cover, weather_std_temp, weather_std_wind = obs
            if species in species_names:
                sums_pres[species] += int(weather_pressure) * int(count_tot)
                amounts[species] += int(count_tot)
                sums_temp[species] += int(weather_temp_day) * int(count_tot)
                # n_temp[species] += int(count_tot)

    _unknown = -99999999999

    for sp, n in amounts.items():
        for sp_list in species_itemsets:
            if sp == sp_list[0]:
                sp_list.append('day temperature %s' % (5 * int(round(sums_temp.get(sp, _unknown) / float(5 * n)))))
                sp_list.append('air pressure %s' % (5 * int(sums_pres.get(sp, _unknown) / float(5 * n))))

    return species_itemsets

