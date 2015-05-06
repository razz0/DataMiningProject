#!/usr/bin/env python3

"""
A module for handling Halias RDF dataset
"""

from rdflib import Graph, RDF, RDFS, Namespace

DATA_DIR = '../data/'
INPUT_DATA_FILES = ['HALIAS4_full.ttl']

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

taxa = taxon_ontology.subjects(RDF.type, nsTaxMeOn["TaxonInChecklist"])
for taxon in taxa:
    labels = taxon_ontology.objects(taxon, RDFS.label)
    if nsRanks["Species"] in taxon_ontology.objects(taxon, RDF.type):
        for label in labels:
            if label.language == 'en':
                print(label)
