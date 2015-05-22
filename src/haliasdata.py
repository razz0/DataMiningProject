#!/usr/bin/env python
"""
Create simple data files from Halias RDF dataset for association analysis
"""


import math
import sys
from collections import defaultdict
import json
import logging

# from joblib import Parallel, delayed

from rdflib import Graph, RDF, RDFS, Namespace
import helpers

logging.basicConfig()

# parser = argparse.ArgumentParser(description='Convert Halias RDF dataset for data mining')
# parser.add_argument('cores', help='How many CPU cores to use (USE 1 FOR NOW)', type=int)
# args = parser.parse_args()

DATA_DIR = '../data/'
INPUT_DATA_FILES = ['HALIAS0_full.ttl',
                    'HALIAS1_full.ttl',
                    'HALIAS2_full.ttl',
                    'HALIAS3_full.ttl',
                    'HALIAS4_full.ttl']

WEATHER_FILE = 'halias_weather_cube.ttl'

nsTaxMeOn = Namespace("http://www.yso.fi/onto/taxmeon/")
nsBio = Namespace("http://www.yso.fi/onto/bio/")
nsRanks = Namespace("http://www.yso.fi/onto/taxonomic-ranks/")
nsHh = Namespace("http://www.hatikka.fi/havainnot/")
nsXSD = Namespace("http://www.w3.org/2001/XMLSchema#")
nsDataCube = Namespace("http://purl.org/linked-data/cube#")
nsDWC = Namespace("http://rs.tdwg.org/dwc/terms/")
nsOWL = Namespace("http://www.w3.org/2002/07/owl#")

nsHalias = Namespace("http://ldf.fi/halias/observations/birds/")
nsHaliasSchema = Namespace("http://ldf.fi/schema/halias/")
#nsHaliasTaxa = Namespace("http://ldf.fi/halias/taxa/")
nsHaliasTaxa = Namespace("http://www.yso.fi/onto/bio/")

taxon_ontology = Graph()
taxon_ontology.parse(DATA_DIR + 'halias_taxon_ontology.ttl', format='turtle')

taxon_map = dict()

taxa = taxon_ontology.subjects(RDF.type, nsTaxMeOn["TaxonInChecklist"])
for taxon in taxa:
    labels = taxon_ontology.objects(taxon, RDFS.label)
#    if nsRanks["Species"] in taxon_ontology.objects(taxon, RDF.type):
    for label in labels:
        if label.language == 'fi':
            taxon_map[str(taxon)] = str(label)
#            print("%s - %s" % (str(taxon), str(label)))
            if ',' in str(label):
                # Not allowed in our basket format
                raise Exception('Illegal character')
#                print(label)

print('Reading data files...')


bird_observation_graph = Graph()
weather_observation_graph = Graph()

for rdf_file in INPUT_DATA_FILES:
    bird_observation_graph.parse(DATA_DIR + rdf_file, format='turtle')
    print(('\tSuccessfully read data file %s' % rdf_file))

weather_observation_graph.parse(DATA_DIR + WEATHER_FILE, format='turtle')
print(('\tSuccessfully read weather data file'))

print(('Got %s statements.' % len(bird_observation_graph)))

observations = bird_observation_graph.subjects(RDF.type, nsDataCube["Observation"])

observation_date = defaultdict(list)
observation_amounts = defaultdict(list)

print('Processing observations...')


for i, observation in enumerate(observations):
    if i % 1000 == 0:
        print('\tObservation %s' % i)

    taxon = next(bird_observation_graph.objects(observation, nsHaliasSchema['observedSpecies']))
    count_mig = next(bird_observation_graph.objects(observation, nsHaliasSchema['countMigration']))
    count_tot = next(bird_observation_graph.objects(observation, nsHaliasSchema['countTotal']))
    month_num = next(bird_observation_graph.objects(observation, nsHaliasSchema['monthOfYear']))

    date = next(bird_observation_graph.objects(observation, nsHaliasSchema['refTime']))

    weather_obs = next(weather_observation_graph.subjects(nsHaliasSchema['refTime'], date), None)

    weather_pressure = float(str(next(weather_observation_graph.objects(weather_obs, nsHaliasSchema['airPressure']), None)))
    weather_cover = float(str(next(weather_observation_graph.objects(weather_obs, nsHaliasSchema['cloudCover']), None)))
    weather_humidity = float(str(next(weather_observation_graph.objects(weather_obs, nsHaliasSchema['humidity']), None)))
    weather_rainfall = float(str(next(weather_observation_graph.objects(weather_obs, nsHaliasSchema['rainfall']), None)))
    weather_temp_day = float(str(next(weather_observation_graph.objects(weather_obs, nsHaliasSchema['temperatureDay']), None)))
    weather_wind = weather_observation_graph.objects(weather_obs, nsHaliasSchema['windDay'])

    weather_std_cover = float(str(next(weather_observation_graph.objects(weather_obs, nsHaliasSchema['standardCloudCover']), None)))
    weather_std_temp = float(str(next(weather_observation_graph.objects(weather_obs, nsHaliasSchema['standardTemperature']), None)))
    weather_std_wind = weather_observation_graph.objects(weather_obs, nsHaliasSchema['standardWind'])

    observation_date[str(date)].append(taxon_map[str(taxon)])

    observation_amounts[str(date)].append((taxon_map[str(taxon)],
                                           count_mig,
                                           count_tot,
                                           month_num,
                                           int(weather_pressure) if not math.isnan(weather_pressure) else None,
                                           int(weather_cover) if not math.isnan(weather_cover) else None,
                                           int(weather_humidity) if not math.isnan(weather_humidity) else None,
                                           int(weather_rainfall) if not math.isnan(weather_rainfall) else None,
                                           int(weather_temp_day) if not math.isnan(weather_temp_day) else None,
                                           [helpers.local_name(str(wind)) for wind in weather_wind],
                                           int(weather_std_cover) if not math.isnan(weather_std_cover) else None,
                                           int(weather_std_temp) if not math.isnan(weather_std_temp) else None,
                                           [helpers.local_name(str(wind)) for wind in weather_std_wind]
                                           ))


print('Writing observations to files...')

f = open(DATA_DIR + 'observation.basket', 'w')

for (date, obs_list) in sorted(observation_date.items()):
    row = ", ".join(obs_list) + "\n"
    #print row
    if sys.version_info < (3, 0):
        f.write(row.encode('utf8'))
    else:
        f.write(row)

f.close()

f = open(DATA_DIR + 'observation.sequence', 'w')

json.dump(observation_amounts, f)

f.close()