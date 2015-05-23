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
    [('peippo', 'Fringilla coelebs', 'chaffinch'), ('mustavaris', 'Corvus frugilegus', 'rook')]
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


def get_species_itemsets(use_all_species=False):
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
            this_species += ['tuntomerkki %s' % local_name(str(chara)) for chara in charas]

            # Take only species with characteristics
        species_itemsets.append(this_species)
        species_names.append(finnish)

    seqs = read_observation_sequences()

    amounts = defaultdict(int)
    sums_pres = defaultdict(int)
    sums_cover = defaultdict(int)
    sums_humi = defaultdict(int)
    sums_rain = defaultdict(int)
    sums_temp = defaultdict(int)

    sums_windsp = defaultdict(int)

    for date, obses in seqs.items():
        for obs in obses:
            species, count_mig, count_tot, month_num, \
                weather_pressure, weather_cover, weather_humidity, weather_rainfall, weather_temp_day, weather_wind_list, \
                weather_std_cover, weather_std_temp, weather_std_wind = obs
            if species in species_names:
                amounts[species] += int(count_tot)
                sums_pres[species] += int(weather_pressure) * int(count_tot)
                if weather_cover is not None:
                    sums_cover[species] += int(weather_cover) * int(count_tot)
                if weather_humidity is not None:
                    sums_humi[species] += int(weather_humidity) * int(count_tot)
                if weather_rainfall is not None:
                    sums_rain[species] += int(weather_rainfall) * int(count_tot)
                sums_temp[species] += int(weather_temp_day) * int(count_tot)
                for wind in weather_wind_list:
                    windspeed = wind[-2:] if wind[-2:].isnumeric() else wind[-1]
                    sums_windsp[species] += int(windspeed)

    pres_list = []
    cover_list = []
    humi_list = []
    rain_list = []
    temp_list = []
    windsp_list = []

    for sp, n in amounts.items():
        pres_list.append(sums_pres[sp] / float(n))
        cover_list.append(sums_cover[sp] / float(n))
        humi_list.append(sums_humi[sp] / float(n))
        rain_list.append(sums_rain[sp] / float(n))
        temp_list.append(sums_temp[sp] / float(n))
        windsp_list.append(sums_windsp[sp] / float(n))

    pres_limit_low = sorted(pres_list)[int(round(len(pres_list) / 3.0))]
    pres_limit_high = sorted(pres_list)[int(round(len(pres_list) / 3.0 * 2))]

    cover_limit_low = sorted(cover_list)[int(round(len(cover_list) / 3.0))]
    cover_limit_high = sorted(cover_list)[int(round(len(cover_list) / 3.0 * 2))]

    humi_limit_low = sorted(humi_list)[int(round(len(humi_list) / 3.0))]
    humi_limit_high = sorted(humi_list)[int(round(len(humi_list) / 3.0 * 2))]

    rain_limit_low = sorted(rain_list)[int(round(len(rain_list) / 3.0))]
    rain_limit_high = sorted(rain_list)[int(round(len(rain_list) / 3.0 * 2))]

    temp_limit_low = sorted(temp_list)[int(round(len(temp_list) / 3.0))]
    temp_limit_high = sorted(temp_list)[int(round(len(temp_list) / 3.0 * 2))]

    windsp_limit_low = sorted(windsp_list)[int(round(len(windsp_list) / 3.0))]
    windsp_limit_high = sorted(windsp_list)[int(round(len(windsp_list) / 3.0 * 2))]

    print('Pressure limits: '
          '\t low = [{min:.2f}, {low:.2f}] \t average = ({low:.2f}, {high:.2f}] \t high = ({high:.2f}, {max:.2f}]'
          .format(min=min(pres_list), low=pres_limit_low, high=pres_limit_high, max=max(pres_list)))
    print('Cloud cover limits: '
          '\t low = [{min:.2f}, {low:.2f}] \t average = ({low:.2f}, {high:.2f}] \t high = ({high:.2f}, {max:.2f}]'
          .format(min=min(cover_list), low=cover_limit_low, high=cover_limit_high, max=max(cover_list)))
    print('Humidity limits: '
          '\t low = [{min:.2f}, {low:.2f}] \t average = ({low:.2f}, {high:.2f}] \t high = ({high:.2f}, {max:.2f}]'
          .format(min=min(humi_list), low=humi_limit_low, high=humi_limit_high, max=max(humi_list)))
    print('Rainfall limits: '
          '\t low = [{min:.2f}, {low:.2f}] \t average = ({low:.2f}, {high:.2f}] \t high = ({high:.2f}, {max:.2f}]'
          .format(min=min(rain_list), low=rain_limit_low, high=rain_limit_high, max=max(rain_list)))
    print('Temperature limits: '
          '\t low = [{min:.2f}, {low:.2f}] \t average = ({low:.2f}, {high:.2f}] \t high = ({high:.2f}, {max:.2f}]'
          .format(min=min(temp_list), low=temp_limit_low, high=temp_limit_high, max=max(temp_list)))
    print('Wind speed limits: '
          '\t low = [{min:.2f}, {low:.2f}] \t average = ({low:.2f}, {high:.2f}] \t high = ({high:.2f}, {max:.2f}]'
          .format(min=min(windsp_list), low=windsp_limit_low, high=windsp_limit_high, max=max(windsp_list)))

    for sp, n in amounts.items():
        for sp_list in species_itemsets:
            if sp == sp_list[0]:
                pressure = sums_pres[sp] / float(n)
                pressure = 'low' if pressure <= pres_limit_low else 'average' if pressure <= pres_limit_high else 'high'
                sp_list.append('air pressure %s' % pressure)

                cover = sums_cover[sp] / float(n)
                cover = 'low' if cover <= cover_limit_low else 'average' if cover <= cover_limit_high else 'high'
                sp_list.append('cloud cover %s' % cover)

                humi = sums_humi[sp] / float(n)
                humi = 'low' if humi <= humi_limit_low else 'average' if humi <= humi_limit_high else 'high'
                sp_list.append('humidity %s' % humi)

                rain = sums_rain[sp] / float(n)
                rain = 'low' if rain <= rain_limit_low else 'average' if rain <= rain_limit_high else 'high'
                sp_list.append('rainfall %s' % rain)

                temp_day = sums_temp[sp] / float(n)
                temp_day = 'low' if temp_day <= temp_limit_low else 'average' if temp_day <= temp_limit_high else 'high'
                sp_list.append('day temperature %s' % temp_day)

                windsp = sums_temp[sp] / float(n)
                windsp = 'low' if windsp <= windsp_limit_low else 'average' if windsp <= windsp_limit_high else 'high'
                sp_list.append('day windspeed %s' % windsp)

    if not use_all_species:
        # Prune species without characteristics
        species_itemsets = [itemset for itemset in species_itemsets if
                            [item for item in itemset if item.startswith('tuntomerkki')]]

    return species_itemsets


def rules_to_tuples(rules_dicts):
    """
    Transform generated rule dicts to tuples

    :param rules_dict:
    :return:
    >>> rulez = [{(('isokoskelo',), ('sinisorsa',)): (0.956, 0.894, 1.013, 0.952)}]
    >>> rules_to_tuples(rulez)
    [(('isokoskelo',), ('sinisorsa',), 0.956, 0.894, 1.013, 0.952)]
    """
    return [list(f.items())[0][0] + list(f.items())[0][1] for f in rules_dicts]