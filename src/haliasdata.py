#!/usr/bin/env python
"""
Create simple data files from Halias RDF dataset for association analysis
"""


import sys
import argparse
from collections import defaultdict
import json
import logging

from joblib import Parallel, delayed

from rdflib import Graph, RDF, RDFS, Namespace

logging.basicConfig()

parser = argparse.ArgumentParser(description='Convert Halias RDF dataset for data mining')
parser.add_argument('cores', help='How many CPU cores to use (USE 1 FOR NOW)', type=int)
args = parser.parse_args()

DATA_DIR = '../data/'
INPUT_DATA_FILES = ['HALIAS0_full.ttl',
                    'HALIAS1_full.ttl',
                    'HALIAS2_full.ttl',
                    'HALIAS3_full.ttl',
                    'HALIAS4_full.ttl']

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

def _read_rdf_file(rdf_file):
    bird_observation_graph.parse(DATA_DIR + rdf_file, format='turtle')
    print(('\tSuccessfully read data file %s' % rdf_file))


Parallel(n_jobs=args.cores)(delayed(_read_rdf_file)(rdf_file) for rdf_file in INPUT_DATA_FILES)

print(('Got %s statements.' % bird_observation_graph))

observations = bird_observation_graph.subjects(RDF.type, nsDataCube["Observation"])

observation_date = defaultdict(list)
observation_amounts = defaultdict(list)

print('Processing observations...')


def _process_observation(i, observation):
    print(i)
    print(observation)
    if i % 1000 == 0:
        print('\tObservation %s' % i)

    taxon = next(bird_observation_graph.objects(observation, nsHaliasSchema['observedSpecies']))
    count_mig = next(bird_observation_graph.objects(observation, nsHaliasSchema['countMigration']))
    count_tot = next(bird_observation_graph.objects(observation, nsHaliasSchema['countTotal']))
    for date in bird_observation_graph.objects(observation, nsHaliasSchema['refTime']):
        observation_date[str(date)].append(taxon_map[str(taxon)])
        observation_amounts[str(date)].append((taxon_map[str(taxon)], count_mig, count_tot))


Parallel(n_jobs=args.cores)(delayed(_process_observation)(index, observation) for index, observation in enumerate(observations))

#import pprint
#pprint.pprint(list(observation_date.items())[:10])

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