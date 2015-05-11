#!/usr/bin/env python

"""
Create simple data files from Halias RDF dataset for association analysis
"""
from collections import defaultdict

from rdflib import Graph, RDF, RDFS, Namespace

DATA_DIR = '../data/'
INPUT_DATA_FILES = ['HALIAS0_full.ttl',
                    'HALIAS1_full.ttl',
                    'HALIAS2_full.ttl',
                    'HALIAS3_full.ttl',
                    'HALIAS4_full.ttl']

nsTaxMeOn = Namespace("http://www.yso.fi/onto/taxmeon/")
#nsEnvirofi = Namespace("http://www.yso.fi/onto/envirofi/")
nsBio = Namespace("http://www.yso.fi/onto/bio/")
nsRanks = Namespace("http://www.yso.fi/onto/taxonomic-ranks/")
nsHh = Namespace("http://www.hatikka.fi/havainnot/")
nsXSD = Namespace("http://www.w3.org/2001/XMLSchema#")
nsDGUIntervals = Namespace("http://reference.data.gov.uk/def/intervals/")
nsDataCube = Namespace("http://purl.org/linked-data/cube#")
nsDWC = Namespace("http://rs.tdwg.org/dwc/terms/")
nsOWL = Namespace("http://www.w3.org/2002/07/owl#")
nsSDMX_A = Namespace("http://purl.org/linked-data/sdmx/2009/attribute#")

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
            taxon_map[unicode(taxon)] = unicode(label)
            print "%s - %s" % (unicode(taxon), unicode(label))
            if ',' in unicode(label):
                # Not allowed in our basket format
                raise Exception('Illegal character')
#                print(label)

print 'Reading data files...'

bird_observation_graph = Graph()
for rdf_file in INPUT_DATA_FILES:
    bird_observation_graph.parse(DATA_DIR + rdf_file, format='turtle')
    print '\tSuccessfully read data file %s' % rdf_file

observations = bird_observation_graph.subjects(RDF.type, nsDataCube["Observation"])

observation_date = defaultdict(list)

print 'Processing %s observations...' % len(observations)

for i, observation in enumerate(observations):
#    for label in bird_observation_graph.objects(observation, RDFS.label):
    if i % 1000 == 0:
        print '\tObservation %s' % i

    taxon = next(bird_observation_graph.objects(observation, nsHaliasSchema['observedSpecies']))
    for date in bird_observation_graph.objects(observation, nsHaliasSchema['refTime']):
        observation_date[str(date)].append(taxon_map[unicode(taxon)])

#import pprint
#pprint.pprint(list(observation_date.items())[:10])

f = open(DATA_DIR + 'observation.basket', 'w')

print 'Writing observations to file...'

for (date, obs_list) in sorted(observation_date.iteritems()):
    row = u", ".join(obs_list) + u"\n"
    #print row
    f.write(row.encode('utf8'))

f.close()